## Why

這套工具目前只能坐在 Mac 前面操作。實際的測試場景卻是「人拿著 iPhone 在走動」——
要調整目的地或中止移動,都得走回電腦旁。iPhone 本身就是被注入定位的那台裝置,
讓它同時擔任遙控器,測試流程才會閉合。

兩件事阻擋了這個用法:

1. **版面在手機上不可用。** 樣式表沒有任何視窗寬度斷點,控制面板是固定 250px 的
   絕對定位浮層,搖桿固定 140×140 貼在右下角。在 375px 寬的螢幕上,面板佔掉約
   三分之二畫面並與搖桿重疊——這同時違反 `control-panel-layout` 自己訂下的
   「面板不得與搖桿重疊」要求。

2. **連線失敗時看不出原因。** 無線通道的建立有多個前提(裝置已配對、開發者模式、
   同網段),任一個不成立就連不上。但目前所有失敗都收斂成同一句
   「No device found via tunneld. Is tunneld running?」。函式庫的
   `_create_rsds_from_tunnels` 會把通道連線逾時靜默跳過並回傳空清單,使得
   「tunneld 沒啟動」「未發現裝置」「已發現裝置但通道連不上」三種需要不同處置的
   狀況無法區分。使用者只能靠反覆嘗試設定位置來反推,無從判斷該接線還是該檢查配對。

## Capabilities

### New Capabilities

- `connection-diagnostics`: 分層探測裝置連線鏈並回報可辨識的階段結果——tunneld 是否可達、
  是否發現裝置、通道能否連上、開發者服務能否開啟——每個階段各自回報成敗與可執行的後續動作。
- `mobile-viewport-layout`: 窄視窗下的版面適配。面板改為底部可收起的形態、控制項符合觸控尺寸、
  搖桿在窄視窗改變尺寸與位置以避免與面板重疊。
- `home-screen-install`: 提供 Web 應用程式資訊清單與 iOS 主畫面圖示,使頁面可加入主畫面並以
  獨立全螢幕模式啟動。

### Modified Capabilities

- `control-panel-layout`: 「面板固定於地圖左側」與「搖桿保持既有尺寸、位置與距邊距離」兩項要求
  目前無視窗寬度條件,窄視窗下與同規格的「面板不得與搖桿重疊」互相矛盾。改為將既有的左側浮層
  形態限定在寬視窗,並將窄視窗形態的責任交給 `mobile-viewport-layout`。
- `joystick-control`: 「搖桿保留既有尺寸與位置」一項改為限定在寬視窗,窄視窗的尺寸與位置由
  `mobile-viewport-layout` 規範。搖桿的手勢擁有權、回應性與可辨識性等要求不變。
- `project-documentation`: 功能涵蓋表須納入本次新增功能的錨點詞——該表是規格的一部分,
  新增功能而不擴充它,會讓「文件涵蓋每一個已實作功能」這條要求在機械檢查下失效。
  另外把關鍵設計決策表的必記項目改為明列,取代目前「最近三個變更所建立的六個決策」這種
  相對指稱:每新增一個變更,「最近三個」所指的集合就改變,同一句話會在不同時間點要求不同內容。

## Impact

- Affected specs:
  - 新增: `connection-diagnostics`, `mobile-viewport-layout`, `home-screen-install`
  - 修改: `control-panel-layout`, `joystick-control`
- Affected code:
  - Modified:
    - app.py — 新增診斷端點,不改動既有的定位與行走端點
    - templates/index.html — 診斷面板標記、資訊清單與 iOS 圖示的 head 參照
    - static/css/style.css — 新增窄視窗斷點與觸控尺寸規則
    - docs/專案簡介.md — 診斷、手機遙控與主畫面安裝的說明,並更新過時的統計數字
    - docs/系統架構設計圖.md — 診斷的資料流與新增的設計決策
    - docs/主要功能程式碼介紹.md — 診斷端點與窄視窗版面的程式碼導覽
  - New:
    - static/manifest.webmanifest — Web 應用程式資訊清單
    - static/icons/app-icon-180.png — iOS 主畫面圖示
    - static/icons/app-icon-512.png — 資訊清單所參照的圖示
    - tools/make_icons.py — 以 Python 標準程式庫產生上述兩個圖示檔,不新增第三方依賴
  - Removed: (none)
- Dependencies: 不新增任何 Python 或前端依賴。診斷端點以標準程式庫的 urllib 直接查詢
  tunneld,並沿用 pymobiledevice3 已公開的 TUNNELD_DEFAULT_ADDRESS 常數,不觸碰其私有函式。
- 不影響裝置寫入路徑: 既有的持久連線、丟棄規則、代次機制與三態回報皆不變動。
