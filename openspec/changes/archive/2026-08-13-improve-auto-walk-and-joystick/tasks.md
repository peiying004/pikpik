## 1. 裝置定位寫入的併發保護（後端）

- [x] 1.1 依「裝置定位寫入以互斥鎖序列化，並丟棄重疊的寫入」決策，讓 `_set_location` 的寫入與重連流程受單一 async 互斥鎖保護，滿足 `Device location writes are mutually exclusive`：任一時刻只有一個協程能建立、替換或關閉 `_dvt` 與 `_location_service`。驗證：移動中拔除裝置再接回，確認伺服器記錄不出現連續不斷的重連訊息，且裝置位置重新跟上標記位置（design 驗收標準第 10 項）。
- [x] 1.2 讓 `_walk_worker` 在前一次裝置寫入尚未完成時跳過本次寫入，滿足 `Overlapping walk writes are dropped rather than queued`：不累積待送佇列，被丟棄的寫入不計為失敗也不回報為錯誤。驗證：執行一趟十分鐘以上的多座標移動，確認裝置位置與網頁標記位置的落差不隨時間持續增大。
- [x] 1.3 取出 `_walk_worker` 派送之寫入協程的例外並記錄到伺服器輸出，滿足 `Device write failures are surfaced, not swallowed` 的伺服器端部分：不再留下未被取用的例外。驗證：移動中中斷裝置連線，確認伺服器端實際印出失敗訊息（現況為完全無輸出）。
- [x] 1.4 確保裝置寫入失敗與重連失敗都不終止移動執行緒，滿足 `Device write failures do not abort the walk`：移動保持 active、插值持續推進、後續週期繼續嘗試寫入。驗證：移動中中斷裝置連線數十秒後接回，確認移動未結束且恢復後裝置位置追上標記位置（design 驗收標準第 9、10 項）。

## 2. 移動狀態回報與預設時速（後端）

- [x] 2.1 依「裝置寫入狀態納入移動狀態回報，使失敗可見」決策，在 `_walk_state` 與 `/api/walk/status` 回應中新增「最近一次裝置寫入是否成功」與「最近一次失敗訊息」兩個欄位。驗證：以 curl 查詢 `/api/walk/status`，確認正常移動時回報成功、中斷裝置後回報失敗並帶訊息、裝置恢復後回報成功。
- [x] 2.2 依「開始移動時同步標記移動狀態，避免前端誤判為已結束」決策，讓 `/api/walk/start` 在回應前即完成 active、進度歸零、總點數與裝置寫入狀態的設定，滿足 `Walk state is truthful when the start request responds`。驗證：啟動移動後立即以 curl 查詢 `/api/walk/status` 確認 active 為真；連續啟動五次移動確認不出現按下開始後立即停止（design 驗收標準第 8 項）。
- [x] 2.3 依「預設時速以後端為權威來源，前端初始化時對齊」決策，將 `_walk_state` 的時速初值與 `/api/walk/start` 的時速 fallback 改為 18，滿足 `Default automatic walk speed` 的後端部分。驗證：以 curl 送出不含時速欄位的 `/api/walk/start`，確認伺服器記錄的移動起始訊息顯示 18 km/h。

## 3. 多座標依序移動（前端）

- [x] 3.1 依「預設時速以後端為權威來源，前端初始化時對齊」決策，將自動移動速度滑桿預設值改為 18，並讓速度顯示文字與 JavaScript 速度變數在頁面初始化時從滑桿當前值推導，滿足 `Default automatic walk speed` 的前端部分。驗證：載入頁面確認標籤顯示 `18 km/h`；不觸碰滑桿即啟動移動，確認伺服器記錄顯示 18 km/h（design 驗收標準第 1 項）。
- [x] 3.2 新增多行座標輸入區與「開始移動」按鈕，並實作解析與驗證，滿足 `Coordinate list input`：忽略空白行與行首行尾空白、拒絕無法解析為兩個數值的行、拒絕緯度超出 -90 至 90 或經度超出 -180 至 180、拒絕有效座標少於兩個，且錯誤訊息指出出錯的輸入行序號與原因。驗證：逐項執行 auto-walk spec 中 `parsing and validation cases` 表格的全部七個案例（涵蓋 design 驗收標準第 4、5 項）。
- [x] 3.3 依「多座標移動採直線分段而非道路路網規劃」、「座標清單直接作為既有走行路線送出，複用插值邏輯」與「起點為第一個座標，開始移動時先定位到該點」三項決策，將解析後的座標清單原封不動作為 route 送至既有 `/api/walk/start`（不呼叫外部路線規劃服務、不展開為密集折線），使移動起點為清單首點，滿足 `Multi-waypoint sequential walk`。驗證：將紅色標記留在遠離首點處，輸入三個相距數百公尺的座標啟動移動，確認裝置直接出現在首點、依序抵達後續座標、中途點不停頓、抵達末點自動結束，且座標未被吸附偏移（design 驗收標準第 2 項）。
- [x] 3.4 繪製依序編號的座標標記與依序連接的折線，並將地圖視野調整至涵蓋全部座標，滿足 `Walk route rendering and progress reporting` 的路線繪製部分。驗證：啟動三座標移動，確認地圖上出現編號 1、2、3 的標記與依序連接的折線，且視野涵蓋全部三個座標。
- [x] 3.5 在移動期間顯示「第 N 點／共 M 點」進度，並在裝置寫入失敗時顯示失敗提示與訊息，滿足 `Walk route rendering and progress reporting` 的進度回報部分與 `Device write failures are surfaced, not swallowed` 的前端部分。驗證：三座標移動中確認進度由第 1 點依序變為第 2、第 3 點（design 驗收標準第 3 項）；中斷裝置連線確認介面於數秒內顯示裝置寫入失敗與訊息，而非維持裝置已連接的外觀（design 驗收標準第 9 項）。
- [x] 3.6 讓停止按鈕中止進行中的多座標移動並清除編號標記與折線，滿足 `Stopping a multi-waypoint walk`。驗證：移動中按下停止，確認移動停止、`/api/walk/status` 回報 active 為否、地圖上的編號標記與折線消失。

## 4. 搖桿修復（前端）

- [x] 4.1 依「搖桿以手勢獨佔解除與地圖的衝突」決策，為搖桿容器宣告不參與瀏覽器預設觸控手勢，並以地圖函式庫提供的工具函式阻擋指標、觸控與滾動事件傳播至底層地圖，滿足 `Joystick owns its gesture`。驗證：以滑鼠與觸控各執行一次搖桿拖曳，確認搖桿跟隨指標、標記持續移動、地圖不因該手勢平移或縮放、頁面不滾動（design 驗收標準第 6 項）。
- [x] 4.2 依「搖桿的地圖跟隨改為無動畫，並移除搖桿容器的背景模糊」決策，將搖桿驅動的地圖跟隨改為不使用動畫的視野設定，並移除搖桿容器的背景模糊效果，滿足 `Joystick movement is responsive and stops on release`。驗證：持續拖曳搖桿十秒確認標記移動無可感知停頓，放開後確認標記在一個更新週期內停止且不繼續飄移（design 驗收標準第 7 項）。
- [x] 4.3 保留搖桿容器的半透明底色、尺寸、位置與既有 CSS 類別名稱，滿足 `Joystick container remains visually distinct`。驗證：在明亮與昏暗的地圖圖磚上各檢視一次，確認搖桿仍可與底下地圖辨別，且位置與尺寸與變更前一致。

## 5. 搖桿函式庫根因修正與前端啟動順序（ingest 補入）

- [x] 5.1 依「修正搖桿函式庫的引用路徑，不改版本」決策，將搖桿函式庫的引用改為該套件實際提供的未最小化檔名（現行引用的最小化檔名回傳 404，`package.json` 指向的才是正確檔名），使搖桿在頁面載入時真正被建立，滿足 `Joystick control is created at page load` 的載入部分。驗證：對頁面引用的該 URL 發出請求確認回傳 200（design 驗收標準第 11 項）；重新載入頁面確認搖桿出現在右下角且可拖動、主控台沒有搖桿函式庫相關錯誤（第 12 項）。
- [x] 5.2 依「僅依賴 DOM 的初始化提前到函式庫初始化之前」決策，將僅依賴 DOM 的初始化（座標讀數與速度標籤的填值）移到宣告區之後、任何第三方函式庫初始化之前，滿足 `DOM-only initialization precedes library-dependent initialization` 與 `Library-independent event bindings survive a library failure`：函式庫失效不再讓這些值留空、也不再讓搜尋框 Enter 鍵與點擊外部關閉結果失效。驗證：硬性重新載入頁面，在未進行任何操作前確認座標讀數顯示數值且速度標籤顯示 `18 km/h`，並在搜尋框按 Enter 確認會執行搜尋（design 驗收標準第 13 項）；比對 page-initialization spec 的 `fresh load with the default slider position` 範例值。
- [x] 5.3 依「函式庫載入失敗必須可見，且不擴散到其餘初始化」決策，在建立搖桿的呼叫外圍加上防護，函式庫不可用時於畫面顯示搖桿不可用的提示並讓其餘初始化繼續完成，滿足 `Third-party library load failure is surfaced` 與 `Joystick control is created at page load` 的降級部分。驗證：暫時把引用改成不存在的路徑後重新載入，確認畫面出現搖桿不可用提示，且速度標籤、座標讀數、搜尋 Enter 鍵、多座標移動全部照常運作，之後把引用改回正確路徑（design 驗收標準第 14 項）。
- [x] 5.4 重新執行第 4 組任務原本無法觀察到的搖桿驗收：在函式庫修正後以滑鼠與觸控各拖曳搖桿一次，確認搖桿跟隨、標記持續移動、地圖不因該手勢平移或縮放、頁面不滾動；並持續拖曳十秒確認無可感知停頓、放開後標記在一個更新週期內停止且不繼續飄移。這些對應 `Joystick owns its gesture` 與 `Joystick movement is responsive and stops on release`，程式碼已於第 4 組寫入但驗收從未真正通過。驗證：design 驗收標準第 6、7 項實際觀察通過；未通過者須回報而非標記完成。
