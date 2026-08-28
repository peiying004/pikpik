#!/bin/bash
# 自動切換到檔案所在的目錄
cd "$(dirname "$0")"

# 明確指定虛擬環境路徑
VENV_PATH="$(pwd)/venv"
VENV_PYTHON="$VENV_PATH/bin/python"
VENV_PMD3="$VENV_PATH/bin/pymobiledevice3"

echo "=== 檢查環境 ==="
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ 找不到虛擬環境中的 Python，請先執行 setup.sh"
    exit 1
fi

# 1. 啟動 tunneld (背景執行)
echo "正在啟動 tunneld..."
sudo "$VENV_PMD3" remote tunneld &
TUNNEL_PID=$!

# 2. 等待隧道建立
sleep 8

# 3. 啟動 GPS 伺服器
echo "正在啟動 GPS 伺服器..."
# 確保使用 venv 裡的 python 執行
"$VENV_PYTHON" app.py

# 當伺服器停止時，關閉 tunneld
kill $TUNNEL_PID 2>/dev/null
