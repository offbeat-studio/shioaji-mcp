# Shioaji MCP 伺服器

提供永豐金證券 Shioaji 交易 API 功能的模型上下文協議 (MCP) 伺服器，透過標準化工具存取交易功能。

**繁體中文** | [English](README_en-US.md)

## 功能特色

### 身份驗證與連線
- `get_account_info` - 取得帳戶資訊和連線狀態

### 市場資料
- `search_contracts` - 根據關鍵字、交易所或類別搜尋交易合約
- `get_snapshots` - 取得指定合約的即時市場快照
- `get_kbars` - 取得合約的歷史 K 線資料

### 交易操作
- `place_order` - 使用指定參數下單買賣（需要權限）
- `cancel_order` - 根據訂單 ID 取消現有訂單（需要權限）
- `list_orders` - 列出所有訂單及其狀態
- `get_positions` - 取得目前持倉和損益
- `get_account_balance` - 取得帳戶餘額和保證金資訊

**⚠️ 交易安全性**：交易操作（`place_order`、`cancel_order`）預設為停用。設定 `SHIOAJI_TRADING_ENABLED=true` 來啟用交易功能。

### 服務條款與合規
- `check_terms_status` - 檢查服務條款簽署狀態和 API 測試完成情況
- `run_api_test` - 執行服務條款合規的 API 測試（登入和訂單測試）

## 必要條件

1. **永豐金證券帳戶**：您需要一個[永豐金證券帳戶](https://www.sinotrade.com.tw/openact)
2. **API 憑證**：申請並取得 API Key 和 Secret Key
3. **服務條款**：完成文件簽署和 API 測試（詳見 [docs/SERVICE_TERMS.md](docs/SERVICE_TERMS.md)）

關於使用 GitHub Container Registry 的 Docker 映像詳細資訊，請參閱 [docs/CONTAINER_REGISTRY.md](docs/CONTAINER_REGISTRY.md)。

## 安裝與使用

### 使用預建的 Docker 映像（建議）

使用 GitHub Container Registry 預建的 Docker 映像是最簡單的方式：

```bash
# 拉取最新穩定版映像
docker pull ghcr.io/musingfox/shioaji-mcp:latest

# 執行 MCP 伺服器（唯讀模式）
docker run --rm -i --platform=linux/amd64 \
  -e SHIOAJI_API_KEY=your_api_key \
  -e SHIOAJI_SECRET_KEY=your_secret_key \
  -e SHIOAJI_TRADING_ENABLED=false \
  ghcr.io/musingfox/shioaji-mcp:latest

# 執行 MCP 伺服器並啟用交易功能
docker run --rm -i --platform=linux/amd64 \
  -e SHIOAJI_API_KEY=your_api_key \
  -e SHIOAJI_SECRET_KEY=your_secret_key \
  -e SHIOAJI_TRADING_ENABLED=true \
  ghcr.io/musingfox/shioaji-mcp:latest
```

#### 可用標籤

- `latest` - 主分支的最新穩定發布版
- `vX.Y.Z`（如 `v0.1.0`）- 特定版本發布
- `dev` - 最新開發版本（可能包含實驗性功能）

生產環境建議使用特定版本標籤。

### 本地建置 Docker 映像

如果偏好本地建置映像：

```bash
# 建置 Docker 映像
docker build -t shioaji-mcp .

# 執行 MCP 伺服器（唯讀模式）
docker run --rm -i --platform=linux/amd64 \
  -e SHIOAJI_API_KEY=your_api_key \
  -e SHIOAJI_SECRET_KEY=your_secret_key \
  -e SHIOAJI_TRADING_ENABLED=false \
  shioaji-mcp
```

### MCP 客戶端設定

在您的 MCP 客戶端中加入以下設定：

```json
{
  "mcpServers": {
    "shioaji": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", "--platform=linux/amd64",
        "-e", "SHIOAJI_API_KEY=your_api_key",
        "-e", "SHIOAJI_SECRET_KEY=your_secret_key",
        "-e", "SHIOAJI_TRADING_ENABLED=false",
        "ghcr.io/musingfox/shioaji-mcp:latest"
      ]
    }
  }
}
```

**交易權限**：
- 設定 `SHIOAJI_TRADING_ENABLED=false`（預設）為唯讀模式
- 設定 `SHIOAJI_TRADING_ENABLED=true` 啟用交易操作

**啟用交易的範例**：
```json
"-e", "SHIOAJI_TRADING_ENABLED=true"
```

開發或測試時，您可以使用 `dev` 標籤：

```json
"ghcr.io/musingfox/shioaji-mcp:dev"
```

### Python 客戶端範例

我們提供 Python 客戶端範例，示範如何程式化使用 Shioaji MCP 伺服器：

```bash
# 安裝 MCP 客戶端程式庫
pip install mcp-client

# 設定您的 API 憑證
export SHIOAJI_API_KEY=your_api_key
export SHIOAJI_SECRET_KEY=your_secret_key

# 執行範例
./examples/python_client.py
```

範例展示：
- 連接到 Shioaji MCP 伺服器
- 取得帳戶資訊
- 搜尋合約
- 取得即時市場資料
- 取得歷史 K 線資料
- 檢索持倉和帳戶餘額

完整程式碼詳見 [examples/python_client.py](examples/python_client.py)。

### 本地開發（Linux/WSL）

```bash
# 複製專案
git clone <repository-url>
cd shioaji-mcp

# 安裝相依套件
uv sync

# 設定環境變數
export SHIOAJI_API_KEY=your_api_key
export SHIOAJI_SECRET_KEY=your_secret_key

# 執行 MCP 伺服器
uv run python -m shioaji_mcp.server
```

## 開發指南

### 環境設定

```bash
# 安裝開發相依套件
uv sync --extra test --extra lint

# 設定環境變數
cp .env.example .env
# 編輯 .env 並填入您的 API 憑證
```

### 測試

```bash
# 執行測試
uv run pytest

# 測試覆蓋率
uv run pytest --cov=src/shioaji_mcp
```

### 程式碼品質

```bash
# 檢查程式碼風格
uv run ruff check src/ tests/

# 格式化程式碼
uv run ruff format src/ tests/
```

### Docker 開發

```bash
# 建置開發 Docker 映像
docker build -t shioaji-mcp-dev .

# 測試 Docker 容器
docker run --rm -i --platform=linux/amd64 \
  -e SHIOAJI_API_KEY=test_key \
  -e SHIOAJI_SECRET_KEY=test_secret \
  shioaji-mcp-dev
```

## 架構

```
src/shioaji_mcp/
├── server.py          # MCP 伺服器主程式
├── tools/             # 工具模組
│   ├── contracts.py   # 合約搜尋
│   ├── market_data.py # 市場資料
│   ├── orders.py      # 訂單操作
│   ├── positions.py   # 持倉查詢
│   └── terms.py       # 服務條款
└── utils/             # 工具程式
    ├── auth.py        # 身份驗證管理
    ├── formatters.py  # 資料格式化
    └── shioaji_wrapper.py # Shioaji 包裝器
```

## 重要注意事項

⚠️ **真實交易 API**
- 此 MCP 伺服器連接到真實的永豐金證券 API
- 所有交易操作都會執行真實訂單
- 請確保您在交易前了解風險
- 建議先以小額進行測試
- 本軟體以「現況」提供，不提供任何形式的保證
- 使用者需負責自己的交易決策和法規遵循

⚠️ **相容性**
- Python 3.10-3.12
- 建議在 Linux 環境或 Docker 中執行
- macOS 使用者應使用 Docker

## 故障排除

### Docker 設定測試

我們提供腳本來測試您的 Docker 設定是否與 Shioaji MCP 伺服器相容：

```bash
# 使腳本可執行
chmod +x scripts/test_docker_setup.sh

# 執行測試腳本
./scripts/test_docker_setup.sh
```

此腳本檢查 Docker 安裝、守護程序狀態、權限、平台支援和基本功能。

### macOS 相依性問題
```bash
# 使用 Docker 解決
docker run --platform=linux/amd64 ...
```

### API 連線問題
```bash
# 檢查環境變數
echo $SHIOAJI_API_KEY
echo $SHIOAJI_SECRET_KEY

# 檢查 API 憑證是否有效
docker run --rm -i --platform=linux/amd64 \
  -e SHIOAJI_API_KEY=your_key \
  -e SHIOAJI_SECRET_KEY=your_secret \
  shioaji-mcp python -c "from shioaji_mcp.utils.auth import auth_manager; print(auth_manager.is_connected())"
```

## 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

## 貢獻

我們歡迎貢獻來改善 Shioaji MCP 伺服器！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何為此專案貢獻的詳細指南。

1. Fork 此專案
2. 建立功能分支
3. 進行變更並加入測試
4. 執行程式碼檢查和測試
5. 提交 Pull Request