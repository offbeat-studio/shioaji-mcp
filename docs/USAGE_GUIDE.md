# Shioaji MCP 使用指南

這份指南介紹如何使用 Shioaji MCP 的各種介面，讓你選擇最適合的方式來操作永豐金證券 API。

## 🎯 三種使用方式

### 1. 互動式命令列工具 (CLI) - 最簡單直覺

適合：日常查詢、快速操作、非程式開發者

```bash
# 安裝
pip install shioaji-mcp

# 設定環境變數
export SHIOAJI_API_KEY=your_api_key
export SHIOAJI_SECRET_KEY=your_secret_key

# 使用命令列工具
shioaji-cli account        # 查詢帳戶資訊
shioaji-cli quote 2330     # 取得台積電即時報價
shioaji-cli search 台積電  # 搜尋股票
shioaji-cli positions      # 查詢持倉
shioaji-cli balance        # 查詢餘額
shioaji-cli history 2330   # 查詢歷史資料
```

#### CLI 常用指令

```bash
# 查詢帳戶
shioaji-cli account

# 取得報價（加上 -d 顯示詳細資訊）
shioaji-cli quote 2330 -d

# 搜尋股票
shioaji-cli search 台積電
shioaji-cli search 2330 --limit 5

# 查詢持倉（可指定帳戶類型）
shioaji-cli positions
shioaji-cli positions --type stock
shioaji-cli positions --type futures

# 查詢餘額
shioaji-cli balance
shioaji-cli balance --type stock

# 查詢歷史資料
shioaji-cli history 2330
shioaji-cli history 2330 --days 90

# 服務條款狀態
shioaji-cli terms status

# 版本資訊
shioaji-cli version
```

### 2. Python SDK - 最適合開發者

適合：自動化交易、資料分析、客製化應用

```python
from shioaji_mcp.sdk import ShioajiSDK

# 初始化（使用環境變數）
sdk = ShioajiSDK()

# 或直接提供金鑰
sdk = ShioajiSDK(api_key="your_key", secret_key="your_secret")

# 取得帳戶資訊
accounts = sdk.get_accounts()

# 搜尋股票
results = sdk.search_stocks("台積電")

# 取得即時報價
quote = sdk.get_quote("2330")
print(f"台積電: ${quote['close']}")

# 取得多支股票報價
quotes = sdk.get_quotes(["2330", "2317", "2454"])

# 取得歷史資料
history = sdk.get_history("2330", days=30)

# 查詢持倉
positions = sdk.get_positions()

# 查詢餘額
balance = sdk.get_balance()

# 使用完畢
sdk.disconnect()
```

#### SDK 範例

我們提供了豐富的範例：

```bash
# 執行 Python 範例
python examples/sdk_example.py

# 使用 Jupyter Notebook（需要安裝 jupyter）
jupyter notebook examples/quickstart_notebook.ipynb
```

### 3. MCP Server - 給 AI 助理使用

適合：Claude Desktop、其他支援 MCP 的 AI 工具

在 Claude Desktop 設定檔中加入：

```json
{
  "mcpServers": {
    "shioaji": {
      "command": "uvx",
      "args": ["shioaji-mcp"],
      "env": {
        "SHIOAJI_API_KEY": "your_api_key",
        "SHIOAJI_SECRET_KEY": "your_secret_key",
        "SHIOAJI_TRADING_ENABLED": "false"
      }
    }
  }
}
```

或使用 Docker：

```json
{
  "mcpServers": {
    "shioaji": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", "--platform=linux/amd64",
        "-e", "SHIOAJI_API_KEY=your_key",
        "-e", "SHIOAJI_SECRET_KEY=your_secret",
        "ghcr.io/musingfox/shioaji-mcp:latest"
      ]
    }
  }
}
```

## 📊 使用場景範例

### 場景 1: 每日監控持倉

使用 CLI 快速查看：

```bash
#!/bin/bash
echo "=== 每日持倉報告 ==="
shioaji-cli positions
echo ""
echo "=== 帳戶餘額 ==="
shioaji-cli balance
```

### 場景 2: 技術分析

使用 Python SDK 進行分析：

```python
from shioaji_mcp.sdk import ShioajiSDK
import pandas as pd
import matplotlib.pyplot as plt

sdk = ShioajiSDK()

# 取得歷史資料
history = sdk.get_history("2330", days=90)
df = pd.DataFrame(history)
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# 計算技術指標
df['MA5'] = df['close'].rolling(window=5).mean()
df['MA20'] = df['close'].rolling(window=20).mean()

# 繪製圖表
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['close'], label='Close')
plt.plot(df.index, df['MA5'], label='MA5')
plt.plot(df.index, df['MA20'], label='MA20')
plt.legend()
plt.show()
```

### 場景 3: 自動化監控

建立監控腳本：

```python
from shioaji_mcp.sdk import ShioajiSDK
import time

sdk = ShioajiSDK()

# 監控名單
watchlist = ["2330", "2317", "2454"]

while True:
    quotes = sdk.get_quotes(watchlist)

    for quote in quotes:
        change_pct = (quote['close'] - quote['open']) / quote['open'] * 100

        # 價格變動超過 3% 時發出通知
        if abs(change_pct) > 3:
            print(f"⚠️  {quote['name']} ({quote['code']}): "
                  f"${quote['close']} ({change_pct:+.2f}%)")

    time.sleep(60)  # 每分鐘檢查一次
```

### 場景 4: 資料匯出

匯出資料到 CSV：

```python
from shioaji_mcp.sdk import ShioajiSDK
import pandas as pd

sdk = ShioajiSDK()

# 取得多支股票的歷史資料
symbols = ["2330", "2317", "2454"]
all_data = []

for symbol in symbols:
    history = sdk.get_history(symbol, days=30)
    df = pd.DataFrame(history)
    df['symbol'] = symbol
    all_data.append(df)

# 合併並匯出
combined_df = pd.concat(all_data)
combined_df.to_csv('stock_history.csv', index=False)
print(f"已匯出 {len(combined_df)} 筆資料到 stock_history.csv")
```

## 🔧 進階設定

### 啟用交易功能

預設為唯讀模式，啟用交易需要：

```bash
export SHIOAJI_TRADING_ENABLED=true
```

### 使用 .env 檔案

建立 `.env` 檔案：

```env
SHIOAJI_API_KEY=your_api_key
SHIOAJI_SECRET_KEY=your_secret_key
SHIOAJI_TRADING_ENABLED=false
```

Python 會自動載入這個檔案。

### 錯誤處理

```python
from shioaji_mcp.sdk import ShioajiSDK

try:
    sdk = ShioajiSDK()
    quote = sdk.get_quote("2330")
except RuntimeError as e:
    print(f"連線錯誤: {e}")
except ValueError as e:
    print(f"參數錯誤: {e}")
except Exception as e:
    print(f"未預期的錯誤: {e}")
```

## 📚 更多資源

### 範例檔案

- `examples/sdk_example.py` - 完整的 SDK 使用範例
- `examples/quickstart_notebook.ipynb` - Jupyter Notebook 互動式教學
- `examples/python_client.py` - MCP 客戶端範例

### 文件

- [README.md](../README.md) - 專案說明
- [CLAUDE.md](../CLAUDE.md) - 專案技術文件
- [CONTRIBUTING.md](../CONTRIBUTING.md) - 貢獻指南

### 外部資源

- [Shioaji 官方文件](https://sinotrade.github.io/)
- [永豐金證券 API 申請](https://www.sinotrade.com.tw/)
- [專案 GitHub](https://github.com/musingfox/shioaji-mcp)

## ⚠️ 重要提醒

1. **保護你的金鑰**：不要將 API 金鑰提交到版本控制系統
2. **測試環境**：建議先在測試環境充分測試後再使用正式環境
3. **風險管理**：所有交易操作都會產生實際訂單，請謹慎使用
4. **服務條款**：使用前請確保已簽署永豐金證券的服務條款

## 🆘 疑難排解

### 連線問題

```
Error: Not connected to Shioaji API
```

解決方法：
1. 檢查環境變數是否正確設定
2. 確認 API 金鑰是否有效（未過期）
3. 檢查網路連線

### 找不到合約

```
Error: Contract XXXX not found
```

解決方法：
1. 使用 `shioaji-cli search` 搜尋正確的股票代碼
2. 確認股票代碼格式正確（通常是 4 位數字）

### 權限問題

```
Error: Trading is disabled
```

解決方法：
1. 設定 `SHIOAJI_TRADING_ENABLED=true` 啟用交易功能
2. 確認帳戶已簽署服務條款

## 💡 最佳實踐

1. **使用環境變數**：不要在程式碼中硬編碼 API 金鑰
2. **錯誤處理**：總是使用 try-except 處理可能的錯誤
3. **資源管理**：使用完畢後記得呼叫 `sdk.disconnect()`
4. **頻率限制**：避免過於頻繁的 API 呼叫
5. **日誌記錄**：記錄重要的操作以便追蹤

## 🎓 學習路徑

1. **初學者**：從 CLI 工具開始，熟悉各種查詢功能
2. **進階使用**：學習使用 Python SDK 進行資料分析
3. **自動化**：建立自動化腳本和監控系統
4. **整合**：將 Shioaji 整合到你的交易策略中

---

如有任何問題或建議，歡迎在 [GitHub Issues](https://github.com/musingfox/shioaji-mcp/issues) 提出。
