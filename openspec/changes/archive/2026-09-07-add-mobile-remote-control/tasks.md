## 1. 診斷端點後端

- [x] 1.1 在 app.py 新增唯讀診斷端點,以 GET 回應 JSON,並實作前兩個階段:查詢 tunneld 的 HTTP 端點判定可達性,再由回應解析裝置清單。位址取自函式庫公開的 TUNNELD_DEFAULT_ADDRESS 常數,查詢以標準程式庫的 urllib 完成,不引入 requests 亦不呼叫任何底線開頭的函式庫私有函式(涵蓋設計決策「診斷以標準程式庫查詢 tunneld,不觸碰函式庫私有函式」、需求 Diagnostics probes the connection chain in four ordered stages、需求 Diagnostics reports the device records it found)。行為:tunneld 未啟動時第一階段回報失敗;tunneld 可達且有裝置時裝置清單每筆帶 UDID、介面位址、通道位址與通道通訊埠,無裝置時為空陣列。驗證:在 tunneld 未啟動下以 curl 請求該端點,確認第一階段為失敗且裝置清單為空陣列;啟動 tunneld 並接上裝置後再次請求,確認裝置清單含至少一筆且四個欄位皆非空。

- [x] 1.2 讓四個階段的結果採「成功／失敗／未執行」三態而非布林,每筆帶階段識別字、顯示名稱、三態結果、細節文字與後續動作文字,且任一階段失敗即停止後續階段並將其標為未執行;四個階段的後續動作文字互不相同。診斷端點在任何階段失敗時仍回應成功狀態碼(涵蓋設計決策「診斷分四個階段,每階段回報可執行的後續動作」、需求 Stage outcomes are three-state rather than boolean、需求 Every stage outcome carries a detail and a next action、需求 Diagnostics endpoint succeeds even when stages fail)。行為:裝置發現失敗時,該階段為失敗、其後兩階段為未執行,且其後續動作文字提及接線、裝置配對、Wi-Fi 同步與開發者模式四項待查條件。驗證:在 tunneld 未啟動下以 curl 請求端點,確認 HTTP 狀態碼為 200、第一階段為失敗、其餘三階段為未執行;比對四筆後續動作文字兩兩不相等。

- [x] 1.3 實作第三與第四階段(通道連線、開發者服務),並使其重用既有的共用連線:共用定位服務已建立時兩階段直接回報成功且不另開連線;尚未建立時沿用既有的連線建立路徑,在序列化定位寫入的同一把裝置鎖保護下進行,連線建立後保留不關閉。診斷全程不寫入座標、不清除模擬定位、不關閉既有連線,亦不改動行走狀態與既有的裝置寫入結果(涵蓋設計決策「診斷不得有副作用,並重用既有的裝置連線」、需求 Diagnostics reuses the existing device connection、需求 Diagnostics leaves device state unchanged)。行為:診斷後若第四階段成功,共用定位服務處於已建立狀態,後續設定位置無須重新建立連線。驗證:啟動行走後連續以 curl 請求診斷端點兩次,再請求行走狀態端點,確認行走仍為進行中、進度持續推進、裝置寫入結果未被診斷結果取代;另確認診斷前後裝置上的模擬座標不變。

- [x] 1.4 在診斷回應中加入伺服器位址欄位,含預設路由對應的主機位址與監聽通訊埠,取得方式為開啟 UDP socket 指定外部目標後讀取本端位址(不送出封包);無法取得時該欄位為空字串且其餘診斷輸出仍完整回報(涵蓋設計決策「回報可從手機存取的伺服器網址」、需求 Diagnostics reports a server address reachable from a phone)。行為:使用者不必自行查詢 Mac 位址即可得知手機端該連的網址。驗證:以 curl 請求端點,確認回應含主機位址與通訊埠 8080;將 Mac 連上 iPhone 個人熱點後再次請求,確認回報的位址落在熱點網段。

## 2. 診斷面板前端

- [x] 2.1 在控制面板新增診斷控制項與結果區,呈現四個階段的顯示名稱、結果、細節與失敗階段的後續動作,並一併呈現伺服器位址與裝置清單;三種階段狀態在視覺上互相可辨,未執行的階段不得呈現為失敗(涵蓋需求 Diagnostics is triggerable from the control interface)。行為:使用者按下診斷後看到四階段各自結果與可執行的後續動作。驗證:在 tunneld 未啟動下觸發診斷,確認畫面顯示一個失敗階段與三個未執行階段,且兩者樣式不同;確認伺服器位址顯示於面板且標示為預設路由位址。

- [x] 2.2 將診斷面板的標記建立與事件繫結排入僅依賴文件的初始化階段,置於任何第三方函式庫初始化之前,使地圖或搖桿函式庫載入失敗時診斷仍可觸發(涵蓋設計決策「診斷面板的初始化歸入僅依賴文件的階段」)。行為:函式庫失效時診斷仍然可用——而函式庫失效正是需要診斷的時機之一。驗證:將地圖函式庫的載入網址改為不存在的路徑後重載頁面,確認診斷控制項仍可觸發並顯示結果。

## 3. 窄視窗版面

- [x] 3.1 在 static/css/style.css 新增以視窗寬度 768 CSS 像素為界的斷點,窄視窗將控制面板改為貼齊視窗底部、橫向佔滿寬度的形態,展開時高度上限為視窗高度的一半並內部捲動,四個區段與其內容全數保留(涵蓋設計決策「窄視窗將面板改為底部抽屜並縮小搖桿」、需求 A narrow viewport is defined by a width breakpoint、需求 Control panel becomes a bottom sheet in a narrow viewport)。行為:375 像素寬下面板位於底部並佔滿寬度;1280 像素寬下維持既有左側浮層。驗證:以瀏覽器開發者工具依序設為 768 與 769 像素寬,確認前者為底部形態、後者為左側形態;在 375×812 下展開面板,確認其高度不超過 406 像素且可內部捲動至最低區段並操作其中控制項。

- [x] 3.2 使控制面板在窄視窗載入時為收起狀態且標題列可見,收起期間面板內容仍留在文件中以供指令稿存取,收起狀態不跨頁面載入保留(涵蓋需求 Control panel is collapsed by default in a narrow viewport)。行為:窄視窗載入後地圖不被面板遮蔽,面板可由標題列展開。驗證:於 375 像素寬載入頁面,確認面板為收起且標題列可見;在收起狀態下啟動多座標移動,確認移動正常進行、進度顯示持有目前座標索引且無元素缺失錯誤。

- [x] 3.3 在窄視窗縮小搖桿並將其上移至面板之上,使搖桿與面板的邊界框在收起與展開兩種狀態下皆不相交,且搖桿完整位於視窗內不被裁切;搖桿保留半透明背景與既有 CSS 類別名稱,並維持在面板之外(涵蓋需求 Panel and joystick do not overlap in a narrow viewport、需求 Joystick container remains visually distinct、需求 Joystick stays outside the panel)。行為:窄視窗下搖桿可操作且不與面板重疊,寬視窗下搖桿的尺寸與位置不變。驗證:於 375 像素寬分別在面板收起與展開時,以 getBoundingClientRect 取得搖桿與面板的邊界框並確認不相交;確認搖桿容器的類別名稱與寬視窗一致且非面板的子節點;於 1280 像素寬確認搖桿仍為 140×140 且位於右下角。

- [x] 3.4 使地圖在窄視窗維持可見與可操作:面板收起時地圖顯示於面板之上,放置目的地無須先收起或關閉任何控制項;面板展開時視窗上半部仍由地圖占用(涵蓋需求 Map stays visible and operable in a narrow viewport)。行為:選定目的地這個必要操作在窄視窗中可直接完成。驗證:於 375 像素寬在面板收起時點按地圖放置目的地並確認成功;展開面板後確認視窗上半部仍為地圖。

- [x] 3.5 使窄視窗下所有以觸控操作的控制項達到最小 44 CSS 像素的觸控目標寬高,涵蓋各區段按鈕、面板收起控制項、診斷控制項、搜尋控制項與停止控制項;兩個速度滑桿的滑塊觸控目標高度亦達 44 CSS 像素(涵蓋需求 Touch targets meet a minimum size in a narrow viewport)。行為:單手觸控可穩定按中每個控制項。驗證:於 375 像素寬以開發者工具逐一量測上列控制項的算繪寬高,確認皆不小於 44 像素;量測滑桿滑塊的觸控高度確認不小於 44 像素。

- [x] 3.6 確認窄視窗版面僅以視窗寬度條件式樣式規則表達,不為兩種寬度提供不同標記,且未改動任何控制項的行為、參數與請求內容;頁面指令稿所存取的元素識別字全數仍可解析,速度標籤與座標讀數的初始化仍先於任何第三方函式庫(涵蓋需求 The narrow-viewport layout preserves control behaviour、需求 Controls are gathered into a single left-side panel)。行為:版面改動不造成任何功能迴歸。驗證:比對頁面標記所宣告的識別字集合與指令稿所存取的識別字集合,確認後者為前者的子集;於 375 像素寬依序操作設定 GPS 位置、置中標記、兩個速度滑桿、座標清單輸入搭配開始移動、停止移動與沿路走到這裡,確認行為與寬視窗一致;確認伺服器對兩種寬度回傳相同標記。

## 4. 加入主畫面

- [x] 4.1 新增 tools/make_icons.py,以 Python 標準程式庫的 zlib 與 struct 產生 static/icons/app-icon-180.png 與 static/icons/app-icon-512.png 兩個純色圓角圖示,不新增任何影像處理依賴,且可重複執行並覆寫既有檔案(涵蓋設計決策「主畫面圖示以 Python 標準程式庫產生」、需求 Icons are generated without adding dependencies)。行為:在圖示檔不存在的檢出中執行該指令稿即可產生兩個尺寸正確的 PNG。驗證:檢視該指令稿的 import 清單確認全數屬於標準程式庫;刪除圖示後執行指令稿,確認兩檔案產生且由 PNG 檔頭讀出的尺寸分別為 180×180 與 512×512;再次執行確認成功覆寫而不報錯。

- [x] 4.2 新增 static/manifest.webmanifest 並自頁面 head 參照,宣告應用名稱、簡稱、standalone 顯示模式、起始網址、背景色、主題色與圖示清單,圖示清單指向 512 像素圖示;起始網址解析後即為模擬器頁面本身(涵蓋需求 A web app manifest is served、需求 The manifest declares standalone display)。行為:資訊清單可經伺服器取得並宣告獨立顯示模式。驗證:以 curl 請求資訊清單路徑,確認取得成功且可解析為 JSON、顯示模式為 standalone、七個欄位皆存在;以 curl 請求其起始網址確認回傳模擬器頁面;以 curl 請求圖示清單中的路徑確認回傳 PNG。

- [x] 4.3 在 templates/index.html 的 head 加入 iOS 主畫面圖示參照(指向 180 像素 PNG)、iOS 獨立網頁應用能力宣告與狀態列樣式宣告,使自主畫面啟動時不保留瀏覽器導覽控制項,且啟動後地圖、控制面板、搖桿、狀態列與診斷控制項全數呈現(涵蓋需求 An iOS home screen icon is provided、需求 Standalone launch presents the full control interface)。行為:經 iOS Safari 分享選單加入主畫面後,由圖示啟動即為無網址列的全螢幕控制介面。驗證:以 curl 請求頁面確認 head 含 iOS 圖示參照、獨立應用能力宣告與狀態列樣式宣告,且圖示路徑回傳 PNG;於 iPhone 上加入主畫面並啟動,確認無網址列且上列五項元素皆在。

## 5. 文件涵蓋

- [x] 5.1 在 docs/專案簡介.md 補上手機遙控、連線診斷與加入主畫面三項功能的說明,並更新已過時的統計數字(後端行數、API 端點數、前端與樣式行數、規格驗收情境數),使其與現況一致。錨點詞 `/api/diagnostics`、`_default_route_address`、`manifest.webmanifest`、44 CSS 像素 至少各出現一次(涵蓋需求 Documentation covers every implemented feature)。行為:讀者從專案簡介就能知道這套工具可用手機遙控、連不上時有分層診斷可查。驗證:以腳本統計上列錨點詞在 docs 目錄的出現次數皆不為零;並比對文中每個統計數字與實際檔案的行數、端點數、情境數相符。

- [x] 5.2 在 docs/系統架構設計圖.md 加入連線診斷的資料流圖,並在關鍵設計決策表補上本次的四項決策(分階段探測且各帶後續動作、重用共用連線而非另開、窄視窗採底部抽屜而非縮窄左側浮層、圖示以標準程式庫產生);分層架構的表現層須列入連線診斷。錨點詞 `_DIAG_STAGE_META`、`_DIAG_NOT_RUN`、`_diag_probe_connection`、`_acquire_rsd`、`--status-bar-h` 至少各出現一次(涵蓋需求 Architecture documentation shows both walk paths、需求 Documentation covers every implemented feature)。行為:架構文件呈現診斷的四個階段如何依序探測並在失敗時停止。驗證:以腳本確認必記決策表的十項決策在文中皆可對應到一列;確認上列錨點詞出現次數不為零;確認多座標依序移動的資料流圖仍不含外部路徑規劃服務。

- [x] 5.3 在 docs/主要功能程式碼介紹.md 加入診斷端點與窄視窗版面的程式碼導覽,以命名負責的函式並說明其職責的方式撰寫,不複製函式本體;錨點詞 `make_icons.py` 至少出現一次(涵蓋需求 Documentation embeds only stable code excerpts、需求 Documentation covers every implemented feature)。行為:讀者能從文件找到診斷各階段由哪個函式負責,而不必先讀完 app.py。驗證:以腳本確認 docs 目錄中沒有任何超過十五行的程式碼區塊;確認三個禁用詞(`timezonefinder`、射後不理、逾時 15 秒)出現次數皆為零;確認四十個錨點詞全部出現。
