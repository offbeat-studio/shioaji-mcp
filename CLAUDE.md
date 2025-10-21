# Shioaji MCP Server - Claude Code 專案配置

## 專案概述

Shioaji MCP Server 是一個提供永豐金證券交易 API 功能的模型上下文協議 (MCP) 伺服器。專案已達到生產就緒狀態，支援完整的交易操作和市場資料存取功能。

### 運行模式

專案支援兩種運行模式：

1. **stdio 模式**（預設）- 標準 MCP 協議，透過標準輸入/輸出通訊
2. **HTTP API 模式**（v0.1.1+）- RESTful API，支援遠端存取和多裝置使用

## 任務管理系統

**配置狀態**: 使用本地 markdown 檔案進行任務管理
- **系統類型**: Claude Code 內建 TodoWrite 工具
- **任務追蹤**: 透過對話中的 todo list 進行即時追蹤
- **狀態同步**: 任務狀態會在每次更新時同步顯示

## 技術棧和工具

### 開發環境
- **Python**: 3.10-3.12
- **套件管理**: `uv` (優先選擇)
- **MCP 框架**: `mcp>=1.0.0`
- **HTTP 框架**: `aiohttp>=3.9.0` (HTTP API 模式)
- **交易 API**: `shioaji==1.2.5`

### 程式碼品質工具
- **代碼檢查**: `ruff` (取代 black, isort, flake8)
- **型別檢查**: `mypy`
- **測試框架**: `pytest` with `pytest-asyncio`

### 部署和分發
- **容器化**: Docker with multi-platform support
- **容器註冊表**: GitHub Container Registry (ghcr.io)
- **CI/CD**: GitHub Actions

## 開發工作流程

### 代碼提交規範
- 使用 conventional commits 格式: `<type>[optional scope]: <description>`
- 例如: `feat(trading): add order cancellation functionality`
- 例如: `fix(auth): resolve connection timeout issues`

### 測試要求
- 所有新功能必須包含對應的單元測試
- 測試覆蓋率應保持在合理水平
- 使用 mock 進行 API 相關測試以避免真實交易

### 安全考量
- **交易安全**: 交易功能預設關閉，需要明確啟用 `SHIOAJI_TRADING_ENABLED=true`
- **憑證管理**: 所有敏感資訊透過環境變數管理
- **權限控制**: 實施分層權限管理系統

## 專案架構

```
src/shioaji_mcp/
├── server.py          # MCP 伺服器主程式
├── tools/             # MCP 工具模組
│   ├── contracts.py   # 合約搜尋工具
│   ├── market_data.py # 市場資料工具  
│   ├── orders.py      # 訂單操作工具
│   ├── positions.py   # 持倉查詢工具
│   └── terms.py       # 服務條款工具
└── utils/             # 共用工具程式
    ├── auth.py        # 身份驗證管理
    ├── formatters.py  # 資料格式化
    ├── permissions.py # 權限管理
    └── shioaji_wrapper.py # Shioaji API 包裝器
```

## 期貨帳戶支援

自版本 0.1.1 起，`get_positions` 和 `get_account_balance` 工具新增期貨帳戶支援：

### 使用範例
```json
// 查詢所有帳戶持倉（預設）
{"account_type": "all"}

// 只查詢股票帳戶
{"account_type": "stock"}

// 只查詢期貨帳戶
{"account_type": "futures"}
```

### 回應格式差異
- **股票持倉**：包含股數、張數計算和持股成本分析
- **期貨持倉**：包含合約數量、保證金和損益資訊
- **期貨餘額**：額外提供維持保證金、初始保證金等期貨特有欄位

## 常用命令

### 開發環境設置
```bash
# 安裝開發相依套件
uv sync --extra dev

# 設定環境變數
export SHIOAJI_API_KEY=your_api_key
export SHIOAJI_SECRET_KEY=your_secret_key
export SHIOAJI_TRADING_ENABLED=false  # 預設唯讀模式
```

### 代碼品質檢查
```bash
# 檢查和修復代碼風格
uv run ruff check --fix src/ tests/
uv run ruff format src/ tests/

# 型別檢查
uv run mypy src/

# 執行測試
uv run pytest
uv run pytest --cov=src/shioaji_mcp  # 包含覆蓋率
```

### Docker 操作
```bash
# 建置本地映像
docker build -t shioaji-mcp .

# 執行容器（唯讀模式）
docker run --rm -i --platform=linux/amd64 \
  -e SHIOAJI_API_KEY=your_key \
  -e SHIOAJI_SECRET_KEY=your_secret \
  -e SHIOAJI_TRADING_ENABLED=false \
  shioaji-mcp

# 使用 GHCR 預建映像
docker pull ghcr.io/musingfox/shioaji-mcp:latest
```

## 專案狀態

**目前版本**: v0.1.0
**開發狀態**: 生產就緒 (Production Ready)
**已實現功能**: 11 個 MCP 工具，涵蓋完整的交易和市場資料功能

### 核心功能
- ✅ 身份驗證和帳戶管理 (3 工具)
- ✅ 市場資料存取 (3 工具) 
- ✅ 交易操作 (3 工具)
- ✅ 持倉和餘額查詢 (2 工具) - **新增期貨帳戶支援**

### 部署方式
- ✅ GitHub Container Registry 分發
- ✅ 多平台 Docker 支援
- ✅ uvx 本地安裝支援

## 重要注意事項

⚠️ **真實交易環境**
- 此專案連接真實的永豐金證券 API
- 所有交易操作都會產生實際訂單
- 建議在生產使用前充分測試
- 使用者需負責自己的交易決策和風險管理

⚠️ **合規要求**
- 需要完成永豐金證券的服務條款簽署
- 必須通過 API 測試驗證
- 遵循相關金融法規要求

## 貢獻指南

1. Fork 專案並創建功能分支
2. 遵循代碼規範和測試要求  
3. 更新相關文件
4. 提交 Pull Request 前確保所有檢查通過
5. 詳細描述變更內容和影響

更多詳細資訊請參閱 [CONTRIBUTING.md](CONTRIBUTING.md)。