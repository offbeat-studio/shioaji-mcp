# Shioaji MCP 範例

這個目錄包含各種使用 Shioaji MCP 的範例程式。

## 📁 檔案說明

### 1. `sdk_example.py` - Python SDK 完整範例

展示如何使用簡化的 Python SDK 進行各種操作。

**執行方式：**
```bash
# 設定環境變數
export SHIOAJI_API_KEY=your_api_key
export SHIOAJI_SECRET_KEY=your_secret_key

# 執行範例
python examples/sdk_example.py
```

**包含功能：**
- 查詢帳戶資訊
- 搜尋股票
- 取得即時報價（單一和多支股票）
- 查詢歷史資料
- 查詢持倉
- 查詢帳戶餘額

### 2. `quickstart_notebook.ipynb` - Jupyter Notebook 教學

互動式教學 notebook，包含資料視覺化和技術分析範例。

**執行方式：**
```bash
# 安裝 Jupyter（如果尚未安裝）
pip install jupyter matplotlib pandas

# 啟動 Jupyter
jupyter notebook examples/quickstart_notebook.ipynb
```

**包含內容：**
- SDK 初始化
- 基本查詢操作
- 資料視覺化（K線圖、成交量圖）
- 技術分析（移動平均線）
- 進階使用技巧

### 3. `python_client.py` - MCP 客戶端範例

展示如何透過 MCP 協議連接和使用 Shioaji MCP Server。

**執行方式：**
```bash
# 安裝 MCP 客戶端（如果尚未安裝）
pip install mcp-client

# 執行範例
python examples/python_client.py
```

**包含功能：**
- 透過 MCP 協議連接 Shioaji Server
- 呼叫 MCP 工具進行各種操作
- 適合整合到 AI 應用中

### 4. MCP 設定檔

#### `mcp_config.json`
基本的 MCP server 設定（唯讀模式）

#### `mcp_config_trading_enabled.json`
啟用交易功能的設定

#### `mcp_config_with_futures.json`
包含期貨帳戶支援的設定

**使用方式：**
```bash
# 複製到 Claude Desktop 設定
# macOS
cp mcp_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows
copy mcp_config.json %APPDATA%\Claude\claude_desktop_config.json
```

## 🎯 快速開始

### 使用 CLI（最簡單）

```bash
# 安裝
pip install shioaji-mcp

# 設定環境變數
export SHIOAJI_API_KEY=your_api_key
export SHIOAJI_SECRET_KEY=your_secret_key

# 開始使用
shioaji-cli account
shioaji-cli quote 2330
shioaji-cli search 台積電
```

### 使用 Python SDK

```python
from shioaji_mcp.sdk import ShioajiSDK

# 初始化
sdk = ShioajiSDK()

# 取得報價
quote = sdk.get_quote("2330")
print(f"台積電: ${quote['close']}")

# 使用完畢
sdk.disconnect()
```

### 使用 Jupyter Notebook

```bash
# 啟動 notebook
jupyter notebook examples/quickstart_notebook.ipynb

# 按照 notebook 中的步驟操作
```

## 📊 使用場景範例

### 場景 1: 建立監控腳本

```python
# monitor.py
from shioaji_mcp.sdk import ShioajiSDK
import time

sdk = ShioajiSDK()
watchlist = ["2330", "2317", "2454"]

while True:
    quotes = sdk.get_quotes(watchlist)
    for quote in quotes:
        change_pct = (quote['close'] - quote['open']) / quote['open'] * 100
        if abs(change_pct) > 3:
            print(f"⚠️  {quote['name']}: {change_pct:+.2f}%")
    time.sleep(60)
```

### 場景 2: 匯出歷史資料

```python
# export_data.py
from shioaji_mcp.sdk import ShioajiSDK
import pandas as pd

sdk = ShioajiSDK()

# 取得多支股票資料
symbols = ["2330", "2317", "2454"]
all_data = []

for symbol in symbols:
    history = sdk.get_history(symbol, days=30)
    df = pd.DataFrame(history)
    df['symbol'] = symbol
    all_data.append(df)

# 匯出 CSV
combined = pd.concat(all_data)
combined.to_csv('stock_data.csv', index=False)
print(f"已匯出 {len(combined)} 筆資料")
```

### 場景 3: 技術分析

```python
# analysis.py
from shioaji_mcp.sdk import ShioajiSDK
import pandas as pd

sdk = ShioajiSDK()

# 取得資料
history = sdk.get_history("2330", days=90)
df = pd.DataFrame(history)
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# 計算技術指標
df['MA5'] = df['close'].rolling(window=5).mean()
df['MA20'] = df['close'].rolling(window=20).mean()
df['MA60'] = df['close'].rolling(window=60).mean()

# 判斷訊號
latest = df.iloc[-1]
if latest['MA5'] > latest['MA20'] > latest['MA60']:
    print("📈 多頭排列")
elif latest['MA5'] < latest['MA20'] < latest['MA60']:
    print("📉 空頭排列")
else:
    print("➡️  盤整")
```

## 🔧 環境設定

### 使用環境變數

```bash
export SHIOAJI_API_KEY=your_api_key
export SHIOAJI_SECRET_KEY=your_secret_key
export SHIOAJI_TRADING_ENABLED=false  # 預設唯讀
```

### 使用 .env 檔案

建立 `.env` 檔案在專案根目錄：

```env
SHIOAJI_API_KEY=your_api_key
SHIOAJI_SECRET_KEY=your_secret_key
SHIOAJI_TRADING_ENABLED=false
```

Python 會自動載入這個檔案。

## ⚠️ 注意事項

1. **API 金鑰安全**：不要將金鑰提交到版本控制系統
2. **唯讀模式**：預設為唯讀模式，不會執行實際交易
3. **測試環境**：建議先在測試環境測試
4. **風險管理**：啟用交易功能時請特別小心

## 📚 更多資源

- [使用指南](../docs/USAGE_GUIDE.md) - 詳細的使用說明
- [專案 README](../README.md) - 專案說明
- [GitHub](https://github.com/musingfox/shioaji-mcp) - 原始碼和問題回報

## 🆘 疑難排解

### 連線錯誤

```
Error: Not connected to Shioaji API
```

**解決方法：**
1. 檢查環境變數是否正確設定
2. 確認 API 金鑰是否有效
3. 檢查網路連線

### 找不到模組

```
ModuleNotFoundError: No module named 'shioaji_mcp'
```

**解決方法：**
```bash
# 重新安裝套件
pip install -e .

# 或使用 uv
uv pip install -e .
```

### 股票代碼錯誤

```
ValueError: Contract XXXX not found
```

**解決方法：**
```bash
# 使用搜尋功能找到正確的代碼
shioaji-cli search 台積電
```

## 💡 建議

1. 從最簡單的 CLI 開始熟悉功能
2. 使用 Jupyter Notebook 學習和實驗
3. 建立自己的自動化腳本
4. 閱讀官方文件了解更多進階功能

---

有問題嗎？歡迎在 [GitHub Issues](https://github.com/musingfox/shioaji-mcp/issues) 提出！
