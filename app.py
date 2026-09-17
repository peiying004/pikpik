import asyncio
import functools
import json
import math
import socket
import threading
import time
import urllib.error
import urllib.request
from flask import Flask, render_template, request, jsonify

from pymobiledevice3.tunneld.api import TUNNELD_DEFAULT_ADDRESS, get_tunneld_devices
from pymobiledevice3.services.dvt.instruments.dvt_provider import DvtProvider
from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation


app = Flask(__name__)

# Global state
current_location = {"lat": 25.033964, "lng": 121.564468}  # Default: Taipei 101
lock = threading.Lock()

# Persistent DVT connection
_dvt = None
_location_service = None
_loop = None
_loop_thread = None

# 序列化所有會建立、替換或關閉 _dvt / _location_service 的流程。
# 移動期間每個週期都會派送一個定位寫入協程，若不互斥，多個協程會同時進入
# _set_location 的重連分支並互相關閉對方剛建好的連線。
_device_lock = asyncio.Lock()

# 單次裝置寫入的上限。超時視為寫入失敗，讓下一個週期能重新嘗試，
# 避免一個永不完成的寫入把後續寫入永久卡住。
_DEVICE_WRITE_TIMEOUT = 15


def _ensure_loop():
    """Ensure a dedicated asyncio event loop running in a background thread."""
    global _loop, _loop_thread
    if _loop is not None and _loop.is_running():
        return
    _loop = asyncio.new_event_loop()
    _loop_thread = threading.Thread(target=_loop.run_forever, daemon=True)
    _loop_thread.start()


def _run_async(coro):
    """Run an async coroutine on the background loop and wait for result."""
    _ensure_loop()
    future = asyncio.run_coroutine_threadsafe(coro, _loop)
    return future.result(timeout=_DEVICE_WRITE_TIMEOUT)


async def _acquire_rsd():
    """取得一條已連線的 RSD 通道。

    拆成獨立的一步，是為了讓診斷能分別判定「通道連不上」與「開發者服務開不起來」
    ——這兩種失敗要做的事不同。函式庫在把通道記錄轉為可用裝置時會靜默跳過連線
    逾時並回傳空清單，因此空清單在已知有通道記錄的前提下就代表通道連不上。
    """
    devices = await get_tunneld_devices()
    if not devices:
        raise RuntimeError("No device found via tunneld. Is tunneld running?")
    return devices[0]


async def _open_developer_service(rsd):
    """在既有的 RSD 通道上開啟 Instruments 通訊與定位模擬服務。"""
    global _dvt, _location_service
    # 1. 先建立 DvtProvider (這層提供 Instruments 通訊能力)
    _dvt = DvtProvider(rsd)
    await _dvt.__aenter__()

    # 2. 將 dvt 實例傳給 LocationSimulation
    _location_service = LocationSimulation(_dvt)
    await _location_service.__aenter__()
    print("✅ 已成功透過 DvtProvider 建立定位模擬服務")


async def _connect():
    """建立包含 DvtProvider 層的連線。"""
    rsd = await _acquire_rsd()
    await _open_developer_service(rsd)

async def _disconnect():
    """依照相反順序正確關閉連線。"""
    global _dvt, _location_service
    # 先關閉定位服務
    if _location_service is not None:
        try:
            await _location_service.__aexit__(None, None, None)
        except Exception:
            pass
    # 再關閉 DVT Provider
    if _dvt is not None:
        try:
            await _dvt.__aexit__(None, None, None)
        except Exception:
            pass
    _dvt = None
    _location_service = None

async def _set_location(lat, lng):
    """Set location on the persistent connection, reconnecting if needed.

    整段（含重連）由 _device_lock 保護，因此任一時刻只有一個協程能建立、
    替換或關閉共用的連線物件。呼叫端契約不變。
    """
    global _location_service
    async with _device_lock:
        if _location_service is None:
            await _connect()
        try:
            await _location_service.set(lat, lng)
        except Exception:
            # Connection stale, reconnect once
            try:
                await _disconnect()
            except Exception:
                pass
            await _connect()
            await _location_service.set(lat, lng)


async def _clear_location():
    """Clear simulated location and close connection."""
    async with _device_lock:
        if _location_service is not None:
            try:
                await _location_service.clear()
            except Exception:
                pass
        await _disconnect()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/location", methods=["GET"])
def get_location():
    return jsonify(current_location)


@app.route("/api/location", methods=["POST"])
def set_location():
    global current_location
    data = request.get_json()
    lat = data.get("lat")
    lng = data.get("lng")
    if lat is None or lng is None:
        return jsonify({"error": "Missing lat/lng"}), 400

    with lock:
        # 強制轉型為數字
        f_lat = float(lat)
        f_lng = float(lng)
        current_location = {"lat": f_lat, "lng": f_lng}
        
        try:
            # 務必傳入轉型後的 f_lat 和 f_lng
            _run_async(_set_location(f_lat, f_lng))
            return jsonify({"status": "ok", "device": True, **current_location})
        except Exception as e:
            return jsonify({"status": "ok", "device": False, "error": str(e), **current_location})


@app.route("/api/stop", methods=["POST"])
def stop_simulation():
    _stop_walk()
    with lock:
        try:
            _run_async(_clear_location())
        except Exception:
            pass
    return jsonify({"status": "stopped"})


# === Connection Diagnostics ===

# 階段結果的三態。not_run 與 failed 必須分開：前者表示前置階段已經失敗、這一階段
# 根本沒有執行，後者表示這一階段真的跑了而且失敗。兩者對使用者的意義與後續動作
# 完全不同，壓成布林正是這個端點要消除的那種歧義。
_DIAG_OK = "ok"
_DIAG_FAILED = "failed"
_DIAG_NOT_RUN = "not_run"

# 診斷查詢 tunneld 的逾時。使用者按下診斷後還在等，所以取得比裝置寫入更短的上限；
# tunneld 在本機，正常情況下是毫秒等級，會用到這個逾時就代表它沒在聽。
_DIAG_HTTP_TIMEOUT = 5

# 監聽通訊埠。診斷要回報手機該連的網址，與 app.run 共用同一個值，避免兩處各寫一次
# 而在改動時走散。
_SERVER_PORT = 8080


def _default_route_address():
    """取得預設路由所對應的本機位址。

    開一個 UDP socket 並指定外部目標，讓作業系統挑出對外的介面後讀回本端位址；
    UDP 的 connect 不送出任何封包，所以這個動作沒有網路副作用。

    只回報預設路由那一個位址，不列舉所有介面——列舉需要第三方套件，與不新增依賴的
    目標衝突。Mac 同時連著多個網路時，回報的位址可能不是使用者預期的那一個，因此
    介面上標示為預設路由位址而非唯一位址。取不到時回空字串，讓其餘診斷照常回報。
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except Exception:
        return ""
    finally:
        sock.close()

# 四個階段的固定順序、顯示名稱與失敗時的後續動作。四筆後續動作文字互不相同：
# 每一種失敗要做的事都不一樣，而把它們壓成同一句正是這個端點要修掉的缺陷。
_DIAG_STAGE_META = [
    (
        "tunneld",
        "tunneld 服務",
        "以 sudo 啟動 tunneld，再重新診斷。",
    ),
    (
        "devices",
        "裝置發現",
        "接上 USB 線；若要無線連線，請確認裝置已與這台 Mac 配對信任、"
        "已在 Finder 啟用透過 Wi-Fi 同步、且已開啟開發者模式。",
    ),
    (
        "tunnel",
        "通道連線",
        "通道已登記但連不上。重新啟動 tunneld；若裝置剛切換過網路，"
        "重新接線可讓通道重新建立。",
    ),
    (
        "developer",
        "開發者服務",
        "確認裝置已開啟開發者模式（設定 → 隱私權與安全性 → 開發者模式），"
        "並已在裝置上信任這台 Mac。",
    ),
]


def _diag_stage(stage_id, name, outcome, detail="", next_action=""):
    """組出一筆階段結果。四個欄位一律存在，未使用時為空字串而不是缺欄位。"""
    return {
        "id": stage_id,
        "name": name,
        "outcome": outcome,
        "detail": detail,
        "next_action": next_action,
    }


def _query_tunneld():
    """向 tunneld 的 HTTP 端點取得通道清單。

    以標準程式庫的 urllib 直接查詢，不呼叫 pymobiledevice3 中底線開頭的私有函式
    ——那是未公開介面，函式庫升版即可能無聲失效。位址取自函式庫已公開的
    TUNNELD_DEFAULT_ADDRESS 常數，不自行寫死。
    """
    host, port = TUNNELD_DEFAULT_ADDRESS
    with urllib.request.urlopen(f"http://{host}:{port}", timeout=_DIAG_HTTP_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _parse_tunnel_records(tunnels):
    """把 tunneld 的回應攤平成裝置清單。

    回應形如 {udid: [{tunnel-address, tunnel-port, interface}, ...]}，同一台裝置
    可能有多筆通道記錄，每筆各自成為一個項目。欄位原樣回報：tunneld 沒有提供
    連線型態，從位址形式反推 USB 或 Wi-Fi 並不可靠，所以不做這個判定。
    """
    devices = []
    for udid, entries in tunnels.items():
        for entry in entries:
            devices.append({
                "udid": udid,
                "interface": entry.get("interface", ""),
                "tunnel_address": entry.get("tunnel-address", ""),
                "tunnel_port": entry.get("tunnel-port", 0),
            })
    return devices


async def _diag_probe_connection():
    """在裝置鎖保護下確認通道與開發者服務可用，並回報是哪一階段失敗。

    共用定位服務已建立時直接回報沿用——既有連線能存在，本身就是通道與開發者服務
    都可用的證據，沒有必要再開一條。尚未建立時走的是正常連線路徑的同兩個步驟，
    並在序列化定位寫入的同一把鎖下進行，因此不會與寫入或彼此並行；建立成功後保留
    連線而不關閉，等同為後續操作暖機。

    回傳 (result, error)，result 為 reused / connected / tunnel_failed /
    developer_failed。
    """
    async with _device_lock:
        if _location_service is not None:
            return "reused", None
        try:
            rsd = await _acquire_rsd()
        except Exception as e:
            return "tunnel_failed", e
        try:
            await _open_developer_service(rsd)
        except Exception as e:
            return "developer_failed", e
        return "connected", None


def _diag_build(results):
    """依固定順序組出四筆階段結果，未填入的階段標為 not_run。

    沒有結果表示前面某一階段已經失敗、這一階段根本沒有執行——這與「跑了而且失敗」
    必須分開表達。後續動作只在失敗時填入，成功與未執行的階段該欄位為空字串。
    """
    stages = []
    for stage_id, name, next_action in _DIAG_STAGE_META:
        outcome, detail = results.get(stage_id, (_DIAG_NOT_RUN, ""))
        stages.append(_diag_stage(
            stage_id, name, outcome, detail,
            next_action if outcome == _DIAG_FAILED else "",
        ))
    return stages


def _diag_response(results, devices):
    """組出診斷回應。

    伺服器位址與階段結果一起回報，因為「我手機該連哪個網址」和「連線鏈通不通」
    是同一個問題的兩半。位址取不到時為空字串，不影響其餘輸出。
    """
    return jsonify({
        "stages": _diag_build(results),
        "devices": devices,
        "server": {"host": _default_route_address(), "port": _SERVER_PORT},
    })


@app.route("/api/diagnostics", methods=["GET"])
def diagnostics():
    """逐階段探測裝置連線鏈，回報每一階段各自的成敗與後續動作。

    這個端點是唯讀的：不寫入座標、不清除模擬定位、不關閉既有連線，也不動走路狀態。
    任一階段失敗時後續階段不執行，但端點本身仍以成功狀態碼回應——階段失敗是診斷的
    正常輸出，不是端點的錯誤。以非 2xx 回應會讓前端無法區分「診斷跑完且發現問題」
    與「診斷自己壞了」。
    """
    host, port = TUNNELD_DEFAULT_ADDRESS
    results = {}
    devices = []

    # 階段一：tunneld 是否可達。
    try:
        tunnels = _query_tunneld()
    except Exception as e:
        results["tunneld"] = (_DIAG_FAILED, f"無法連上 tunneld（{host}:{port}）：{e}")
        return _diag_response(results, devices)

    results["tunneld"] = (_DIAG_OK, f"已連上 tunneld（{host}:{port}）。")

    # 階段二：tunneld 是否發現裝置。
    devices = _parse_tunnel_records(tunnels)
    if not devices:
        results["devices"] = (_DIAG_FAILED, "tunneld 可達，但沒有回報任何裝置。")
        return _diag_response(results, devices)

    results["devices"] = (_DIAG_OK, f"發現 {len(devices)} 筆通道記錄。")

    # 階段三與階段四：通道連線與開發者服務。兩者共用一次探測——沿用既有連線時
    # 兩階段一起成立，重新建立時則能分辨是哪一步失敗。
    try:
        probe, err = _run_async(_diag_probe_connection())
    except Exception as e:
        # 探測本身沒跑完（例如逾時），這一階段沒有結果可言，記為失敗並停在這裡。
        results["tunnel"] = (_DIAG_FAILED, f"探測連線時中斷：{e}")
        return _diag_response(results, devices)

    if probe == "tunnel_failed":
        results["tunnel"] = (_DIAG_FAILED, f"通道無法連上：{err}")
        return _diag_response(results, devices)

    if probe == "developer_failed":
        results["tunnel"] = (_DIAG_OK, "通道連線正常。")
        results["developer"] = (_DIAG_FAILED, f"開發者服務無法開啟：{err}")
        return _diag_response(results, devices)

    if probe == "reused":
        detail = "沿用既有的定位服務連線，未另開連線。"
    else:
        detail = "已建立連線並保留。"
    results["tunnel"] = (_DIAG_OK, "通道連線正常。")
    results["developer"] = (_DIAG_OK, detail)

    return _diag_response(results, devices)


# === Auto Walk (server-side) ===
_DEFAULT_WALK_SPEED_KMH = 18

_walk_thread = None
_walk_stop_event = threading.Event()
_walk_state = {
    "active": False,
    "lat": 0,
    "lng": 0,
    "speed_kmh": _DEFAULT_WALK_SPEED_KMH,
    "progress": 0,
    "total": 0,
    # 最近一次裝置寫入的結果，三態：None 表示這一輪還沒有任何寫入結果、True 成功、
    # False 失敗。device_error 只在 False 時帶原因，另外兩態為空字串。移動中的
    # lat/lng 是純數學插值，與裝置寫入成敗無關；沒有這兩個欄位，裝置早已凍結時
    # 介面仍會顯示一切正常。
    # 用 None 而不是預設 True：走路剛開始時第一次寫入的結果還沒回來，預設 True
    # 會讓前端第一次輪詢就在毫無根據的情況下宣稱裝置已連接。
    "device_ok": None,
    "device_error": "",
}

# 移動期間是否已有一個裝置寫入尚未完成。旗標由移動執行緒設為 True、由 event
# loop 執行緒在完成回呼中清除；單一 bool 賦值在 GIL 下為原子操作。
_walk_write_inflight = False

# 最後一次「成功完成」的裝置寫入所帶的座標，走路開始時重設為 None。終點補寫用
# 它判斷路線的最後一個座標是否已經真的送達，而不是去猜哪一個週期是最後一個。
_walk_last_sent = None

# 走路的代次編號，每次走路開始時遞增。裝置寫入是非同步的，停止走路只等待工作
# 執行緒結束、不等也不取消已派送的寫入協程，所以上一輪的寫入可能在新一輪開始
# 之後才完成。沒有代次，那筆結果會覆寫新一輪剛重設的「尚未有結果」。
_walk_generation = 0


def _on_walk_write_done(generation, clears_inflight, lat, lng, future):
    """取出寫入協程的結果，讓例外不再被無人取用的 Future 吞掉。

    generation 是派送當下的走路代次。與當前代次不符表示這筆結果屬於已經被取代
    的那一輪走路，整筆丟棄。

    clears_inflight 表示這次派送當初有沒有把進行中旗標設起來。起點與終點的
    寫入是丟棄規則的例外、不持有那個旗標，因此也不該在完成時把它放掉 ——
    否則會誤放掉某個中段寫入正持有的旗標。
    """
    global _walk_write_inflight, _walk_last_sent

    if generation != _walk_generation:
        # 過期代次：不寫入走路狀態、不記錄失敗、也不改動進行中旗標。仍然把結果
        # 取出來，因為「每一次寫入的例外都必須被取用」是既有的規格要求。
        try:
            exc = future.exception()
        except Exception as e:
            exc = e
        if exc is not None:
            print(f"[Walk] 丟棄過期代次 {generation} 的寫入失敗: {exc}")
        return

    if clears_inflight:
        _walk_write_inflight = False
    try:
        future.result()
    except Exception as e:
        message = str(e) or type(e).__name__
        _walk_state["device_ok"] = False
        _walk_state["device_error"] = message
        print(f"[Walk] 裝置寫入失敗: {message}")
    else:
        _walk_last_sent = (lat, lng)
        _walk_state["device_ok"] = True
        _walk_state["device_error"] = ""


def _dispatch_walk_write(lat, lng, generation, respect_inflight=True):
    """派送一次走路路徑上的裝置寫入，回傳是否真的派送出去。

    respect_inflight 為 True 時套用「前一次寫入尚未完成就丟棄本次」的規則，
    這是移動期間每個週期的行為。路線的起點與終點以 False 呼叫 —— 它們是這條
    規則僅有的兩個具名例外：起點不該因為剛好有前一次寫入未完成而被略過，終點
    之後也沒有下一個週期可以補救。
    """
    global _walk_write_inflight

    if respect_inflight and _walk_write_inflight:
        return False

    try:
        _ensure_loop()
        if respect_inflight:
            _walk_write_inflight = True
        future = asyncio.run_coroutine_threadsafe(
            asyncio.wait_for(_set_location(lat, lng), _DEVICE_WRITE_TIMEOUT),
            _loop,
        )
        future.add_done_callback(
            functools.partial(_on_walk_write_done, generation, respect_inflight, lat, lng)
        )
        return True
    except Exception as e:
        # 排程本身失敗：旗標必須放掉，否則後續週期永遠不再嘗試寫入。
        if respect_inflight:
            _walk_write_inflight = False
        message = str(e) or type(e).__name__
        # 派送失敗同樣只在代次相符時才記錄，理由與完成回呼相同。
        if generation == _walk_generation:
            _walk_state["device_ok"] = False
            _walk_state["device_error"] = message
        print(f"[Walk] 裝置寫入派送失敗: {message}")
        return False


def _haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    to_rad = math.radians
    dlat = to_rad(lat2 - lat1)
    dlng = to_rad(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _walk_worker(route_coords, speed_kmh, generation):
    """在背景執行緒中沿 route_coords 依 speed_kmh 插值前進。

    移動中狀態、進度與總點數由 /api/walk/start 在回應前設定，這裡不重複設定。
    裝置寫入的成敗完全不影響這個迴圈：寫入以協程派送，其例外在完成回呼中處理，
    因此寫入失敗或重連失敗都不會中斷移動。
    """
    global current_location, _walk_write_inflight

    lat, lng = route_coords[0]
    walk_index = 0
    interval = 0.2  # 200ms per tick
    tick_count = 0

    print(f"[Walk] 開始移動, 路線點數: {len(route_coords)}, 速度: {speed_kmh} km/h")

    # 起點寫入：在產生任何插值位置之前，先把路線的第一個座標送到裝置。先前這裡
    # 沒有寫入，迴圈的第一個週期會先前進一個週期的距離才第一次寫入，裝置因此
    # 從來沒有真正到過路線的起點（18 km/h 下差一公尺，速度愈高差愈多）。
    _dispatch_walk_write(lat, lng, generation, respect_inflight=False)

    try:
        while not _walk_stop_event.is_set() and walk_index < len(route_coords) - 1:
            tick_start = time.monotonic()

            meters_per_tick = (speed_kmh * 1000 / 3600) * interval
            remaining = meters_per_tick

            while remaining > 0 and walk_index < len(route_coords) - 1:
                lat2, lng2 = route_coords[walk_index + 1]
                dist_to_next = _haversine(lat, lng, lat2, lng2)

                if dist_to_next <= remaining:
                    lat, lng = lat2, lng2
                    remaining -= dist_to_next
                    walk_index += 1
                else:
                    fraction = remaining / dist_to_next if dist_to_next > 0 else 0
                    lat += (lat2 - lat) * fraction
                    lng += (lng2 - lng) * fraction
                    remaining = 0

            # Update state (no lock needed for simple assignments)
            current_location = {"lat": lat, "lng": lng}
            _walk_state["lat"] = lat
            _walk_state["lng"] = lng
            _walk_state["progress"] = walk_index

            # Send to device. 前一次寫入尚未完成時直接丟棄本次寫入 —— 座標以每個
            # 週期約一公尺推進，較新的座標已包含較舊座標的資訊，而無上界排隊會讓
            # 裝置位置離顯示位置愈來愈遠。丟棄不計為失敗、不回報為錯誤。
            _dispatch_walk_write(lat, lng, generation)

            tick_count += 1
            if tick_count % 25 == 0:  # Log every ~5 seconds
                print(f"[Walk] 進度: {walk_index}/{len(route_coords)}, 位置: {lat:.6f}, {lng:.6f}")

            # Sleep precisely
            elapsed = time.monotonic() - tick_start
            sleep_time = max(0, interval - elapsed)
            if sleep_time > 0:
                _walk_stop_event.wait(sleep_time)

        # 終點補寫：走完全程時，若路線的最後一個座標還沒成功送達就補派送一次，
        # 同樣不受丟棄規則限制。抵達終點的那個週期若正好有前一次寫入尚未完成，
        # 本次寫入會被丟棄，而迴圈條件在同一刻不再成立 —— 沒有這段補寫，介面
        # 顯示已抵達終點，裝置卻停在終點前的某個位置。
        # 判斷依據是「最後成功送達的座標是否等於路線終點」而不是「這是不是最後
        # 一個週期」：迴圈也可能因為停止事件提早結束，用前者兩種收尾都正確。
        # 使用者按下停止時不補寫 —— 使用者要的是停在當下，不是被推到終點。
        if not _walk_stop_event.is_set():
            final_point = tuple(route_coords[-1])
            if _walk_last_sent != final_point:
                _dispatch_walk_write(final_point[0], final_point[1], generation, respect_inflight=False)
    finally:
        # 無論正常走完、被停止、或迴圈本身拋錯，移動中狀態都必須歸零，
        # 否則前端會永遠看到 active 為真。
        _walk_state["active"] = False
        print(f"[Walk] 移動結束, 最終位置: {lat:.6f}, {lng:.6f}")


def _stop_walk():
    global _walk_thread
    _walk_stop_event.set()
    if _walk_thread and _walk_thread.is_alive():
        _walk_thread.join(timeout=2)
    _walk_thread = None
    _walk_state["active"] = False


def _parse_walk_request(data):
    """把走路開始請求轉為數值路線與速度，或回傳一則錯誤說明。

    回傳 (coords, speed, error)：error 不為 None 時另外兩個值沒有意義。

    驗證必須在啟動工作執行緒之前完成。先前只有狀態欄位取用了轉型後的第一個
    座標，交給工作執行緒的是原封不動的輸入 —— 座標若是字串，距離計算會在背景
    執行緒拋出型別錯誤、執行緒當場結束、收尾邏輯把移動中狀態設為否，前端第一次
    輪詢讀到未移動就送出停止請求。使用者看到的是「按下開始卻馬上停下」，與真正
    的成因毫無關聯。
    """
    route = data.get("route", [])  # [[lat, lng], ...]
    if not isinstance(route, list) or len(route) < 2:
        return None, None, "Route too short"

    coords = []
    for i, point in enumerate(route):
        position = i + 1
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            return None, None, f"Route point {position} is not a [lat, lng] pair"
        try:
            lat = float(point[0])
            lng = float(point[1])
        except (TypeError, ValueError):
            return None, None, f"Route point {position} is not a pair of numbers"
        if not math.isfinite(lat) or not math.isfinite(lng):
            return None, None, f"Route point {position} is not a pair of finite numbers"
        if not -90 <= lat <= 90:
            return None, None, f"Route point {position} latitude {lat} is outside -90..90"
        if not -180 <= lng <= 180:
            return None, None, f"Route point {position} longitude {lng} is outside -180..180"
        coords.append((lat, lng))

    try:
        speed = float(data.get("speed_kmh", _DEFAULT_WALK_SPEED_KMH))
    except (TypeError, ValueError):
        return None, None, "Speed is not a number"
    if not math.isfinite(speed) or speed <= 0:
        return None, None, "Speed must be greater than 0"

    return coords, speed, None


@app.route("/api/walk/start", methods=["POST"])
def start_walk():
    global _walk_thread, _walk_write_inflight, _walk_last_sent, _walk_generation

    # 驗證排在停止前一輪走路之前：被拒絕的請求不得動到任何走路狀態，而停止
    # 走路本身就會把移動中狀態設為否。
    coords, speed, error = _parse_walk_request(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400

    _stop_walk()
    _walk_stop_event.clear()

    # 移動中狀態必須在回應前就為真，否則前端一收到回應就開始輪詢，可能搶在
    # 背景執行緒設定狀態之前讀到「未移動」而立刻送出停止請求 —— 使用者看到的
    # 是按下開始卻馬上停下。同時清掉上一輪殘留的進度與裝置寫入狀態。
    # 代次先遞增：此後上一輪派送的寫入完成時就對不上號，會被整筆丟棄。
    _walk_generation += 1
    _walk_write_inflight = False
    _walk_last_sent = None
    _walk_state["active"] = True
    _walk_state["speed_kmh"] = speed
    _walk_state["progress"] = 0
    _walk_state["total"] = len(coords)
    _walk_state["lat"] = coords[0][0]
    _walk_state["lng"] = coords[0][1]
    # 回到「尚未有結果」，而不是預設成功：這一輪的第一次寫入還沒派送。
    _walk_state["device_ok"] = None
    _walk_state["device_error"] = ""

    _walk_thread = threading.Thread(
        target=_walk_worker, args=(coords, speed, _walk_generation), daemon=True
    )
    _walk_thread.start()

    return jsonify({"status": "walking", "points": len(coords)})


@app.route("/api/walk/stop", methods=["POST"])
def stop_walk():
    _stop_walk()
    return jsonify({"status": "stopped"})


@app.route("/api/walk/status", methods=["GET"])
def walk_status():
    return jsonify(_walk_state)


if __name__ == "__main__":
    # 綁定所有介面是功能需求（同網段的手機與瀏覽器要連得到這台機器），但互動式
    # 除錯器不是 —— 兩者同時開啟等於把任意程式碼執行的入口開放給同網段。
    app.run(host="0.0.0.0", port=_SERVER_PORT, debug=False)
