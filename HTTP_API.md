# Shioaji MCP Server - HTTP API 使用指南

## 概述

Shioaji MCP Server 現在支援 HTTP API 模式，讓您可以透過 HTTP 請求來使用所有 MCP 功能。這個模式特別適合：

- 從手機/平板存取
- 建立自訂客戶端應用程式
- 在 Tailscale VPN 環境中使用
- 需要 RESTful API 介面的場景

## 安全特性

- ✅ API Key 驗證（Bearer Token）
- ✅ 可配置監聽地址（支援 Tailscale IP）
- ✅ 請求日誌記錄
- ✅ Non-root 用戶運行（Docker）

---

## 快速開始

### 1. 環境變數配置

HTTP 模式需要以下環境變數：

```bash
# Shioaji API 憑證（必填）
export SHIOAJI_API_KEY="your_api_key"
export SHIOAJI_SECRET_KEY="your_secret_key"

# HTTP API 配置（必填）
export HTTP_API_KEY="your_secure_api_key_here"

# HTTP 伺服器配置（選填）
export HTTP_LISTEN_HOST="127.0.0.1"  # 預設：127.0.0.1
export HTTP_LISTEN_PORT="8080"       # 預設：8080

# 交易權限（選填，預設關閉）
export SHIOAJI_TRADING_ENABLED="false"
```

### 2. 使用 Docker 運行

#### 本地開發（只監聽 localhost）

```bash
docker run --rm -p 127.0.0.1:8080:8080 \
  -e MCP_MODE=http \
  -e SHIOAJI_API_KEY="your_api_key" \
  -e SHIOAJI_SECRET_KEY="your_secret_key" \
  -e HTTP_API_KEY="your_secure_api_key" \
  -e HTTP_LISTEN_HOST="0.0.0.0" \
  -e HTTP_LISTEN_PORT="8080" \
  shioaji-mcp:latest
```

#### Tailscale 環境（監聽 Tailscale IP）

```bash
# 先取得 Tailscale IP
TAILSCALE_IP=$(tailscale ip -4)

# 運行容器
docker run --rm -p ${TAILSCALE_IP}:8080:8080 \
  -e MCP_MODE=http \
  -e SHIOAJI_API_KEY="your_api_key" \
  -e SHIOAJI_SECRET_KEY="your_secret_key" \
  -e HTTP_API_KEY="your_secure_api_key" \
  -e HTTP_LISTEN_HOST="0.0.0.0" \
  -e HTTP_LISTEN_PORT="8080" \
  shioaji-mcp:latest
```

### 3. 本地安裝運行

```bash
# 安裝套件（包含 HTTP 支援）
uv pip install -e .

# 設定環境變數
export SHIOAJI_API_KEY="your_api_key"
export SHIOAJI_SECRET_KEY="your_secret_key"
export HTTP_API_KEY="your_secure_api_key"

# 啟動 HTTP 伺服器
shioaji-mcp-http
```

---

## API 端點

### 1. 健康檢查

**端點：** `GET /health`
**認證：** 不需要

**回應範例：**
```json
{
  "status": "healthy",
  "connected": true,
  "version": "0.1.0"
}
```

**使用範例：**
```bash
curl http://localhost:8080/health
```

---

### 2. 列出可用工具

**端點：** `GET /api/tools/list`
**認證：** 需要 API Key

**Headers：**
```
Authorization: Bearer your_api_key_here
```

**回應範例：**
```json
{
  "success": true,
  "tools": [
    {
      "name": "get_account_info",
      "description": "Get account information",
      "inputSchema": {...}
    },
    ...
  ]
}
```

**使用範例：**
```bash
curl -H "Authorization: Bearer your_api_key" \
  http://localhost:8080/api/tools/list
```

---

### 3. 執行工具

**端點：** `POST /api/tools/call`
**認證：** 需要 API Key
**Content-Type：** application/json

**請求格式：**
```json
{
  "tool": "tool_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**回應格式：**
```json
{
  "success": true,
  "data": {...},
  "message": "操作成功訊息"
}
```

**錯誤回應：**
```json
{
  "success": false,
  "error": "錯誤訊息"
}
```

---

## 使用範例

### 範例 1：取得帳戶資訊

```bash
curl -X POST http://localhost:8080/api/tools/call \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_account_info",
    "arguments": {}
  }'
```

**回應：**
```json
{
  "success": true,
  "data": [
    {
      "account_id": "1234567",
      "broker_id": "9A95",
      "account_type": "S",
      "account_type_parsed": "stock",
      "signed": true,
      "is_stock_account": true,
      "is_futures_account": false
    }
  ],
  "message": "Retrieved 1 account(s) information"
}
```

---

### 範例 2：搜尋合約

```bash
curl -X POST http://localhost:8080/api/tools/call \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "search_contracts",
    "arguments": {
      "keyword": "台積電"
    }
  }'
```

---

### 範例 3：取得即時報價

```bash
curl -X POST http://localhost:8080/api/tools/call \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_snapshots",
    "arguments": {
      "contracts": ["2330"]
    }
  }'
```

---

### 範例 4：取得持倉資訊

```bash
curl -X POST http://localhost:8080/api/tools/call \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_positions",
    "arguments": {
      "account_type": "all"
    }
  }'
```

---

### 範例 5：取得 K 線資料

```bash
curl -X POST http://localhost:8080/api/tools/call \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_kbars",
    "arguments": {
      "contract": "2330",
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    }
  }'
```

---

## Python 客戶端範例

```python
import requests

class ShioajiHTTPClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def call_tool(self, tool: str, arguments: dict = None):
        """執行 MCP 工具"""
        response = requests.post(
            f"{self.base_url}/api/tools/call",
            headers=self.headers,
            json={
                "tool": tool,
                "arguments": arguments or {}
            }
        )
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        """列出可用工具"""
        response = requests.get(
            f"{self.base_url}/api/tools/list",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def health_check(self):
        """健康檢查"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

# 使用範例
client = ShioajiHTTPClient(
    base_url="http://localhost:8080",
    api_key="your_api_key"
)

# 取得帳戶資訊
account_info = client.call_tool("get_account_info")
print(account_info)

# 搜尋合約
contracts = client.call_tool("search_contracts", {"keyword": "台積電"})
print(contracts)
```

---

## JavaScript/TypeScript 客戶端範例

```typescript
class ShioajiHTTPClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async callTool(tool: string, args: Record<string, any> = {}) {
    return this.request('/api/tools/call', {
      method: 'POST',
      body: JSON.stringify({ tool, arguments: args }),
    });
  }

  async listTools() {
    return this.request('/api/tools/list');
  }

  async healthCheck() {
    return this.request('/health');
  }
}

// 使用範例
const client = new ShioajiHTTPClient(
  'http://localhost:8080',
  'your_api_key'
);

// 取得帳戶資訊
const accountInfo = await client.callTool('get_account_info');
console.log(accountInfo);
```

---

## 可用工具列表

| 工具名稱 | 說明 | 必要參數 |
|---------|------|---------|
| `get_account_info` | 取得帳戶資訊 | - |
| `search_contracts` | 搜尋合約 | - |
| `get_snapshots` | 取得即時報價 | `contracts` |
| `get_kbars` | 取得 K 線資料 | `contract` |
| `get_positions` | 取得持倉 | - |
| `get_account_balance` | 取得帳戶餘額 | - |
| `list_orders` | 列出訂單 | - |
| `place_order` | 下單 | `contract`, `action`, `quantity` |
| `cancel_order` | 取消訂單 | `order_id` |
| `check_terms_status` | 檢查服務條款狀態 | - |
| `run_api_test` | 執行 API 測試 | - |

詳細參數說明請使用 `GET /api/tools/list` 查詢。

---

## 安全性建議

### 1. API Key 管理
- ✅ 使用強隨機字串（建議 32+ 字元）
- ✅ 定期更換 API Key
- ✅ 不要在程式碼中硬編碼
- ✅ 使用環境變數或密鑰管理工具

### 2. 網路安全
- ✅ 只在 Tailscale VPN 內使用
- ✅ 不要暴露到公網
- ✅ 使用防火牆限制存取
- ✅ 考慮加上 HTTPS（使用 reverse proxy）

### 3. 交易安全
- ✅ 交易功能預設關閉
- ✅ 需要時才啟用 `SHIOAJI_TRADING_ENABLED=true`
- ✅ 記錄所有交易操作
- ✅ 定期審查交易日誌

### 4. 監控建議
- ✅ 定期檢查 `/health` 端點
- ✅ 監控異常請求
- ✅ 設定告警機制
- ✅ 保留存取日誌

---

## 常見問題

### Q1: 如何生成安全的 API Key？

**Linux/macOS:**
```bash
openssl rand -hex 32
```

**Python:**
```python
import secrets
print(secrets.token_hex(32))
```

---

### Q2: 如何在 Tailscale 環境中使用？

1. 確保伺服器和客戶端都在同一個 Tailscale 網路
2. 設定 `HTTP_LISTEN_HOST="0.0.0.0"`
3. 使用 Tailscale IP 存取服務
4. 確保防火牆只允許 Tailscale 流量

---

### Q3: 如何啟用 HTTPS？

建議使用 reverse proxy（如 nginx 或 Caddy）：

```nginx
# nginx 範例
server {
    listen 443 ssl;
    server_name your-tailscale-hostname;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Authorization $http_authorization;
    }
}
```

---

### Q4: 如何從手機存取？

1. 在手機安裝 Tailscale app
2. 連接到同一個 Tailscale 網路
3. 使用 HTTP 客戶端 app（如 Postman、HTTPBot）
4. 或開發自訂的行動應用程式

---

## 效能考量

- **並發請求：** aiohttp 支援高並發
- **回應時間：** 通常 < 1 秒（取決於網路和 API）
- **連線限制：** 預設無限制（可透過 aiohttp 配置）
- **逾時設定：** 建議設定適當的 timeout

---

## 故障排除

### 問題：401 Unauthorized

**原因：** API Key 錯誤或缺失

**解決：**
```bash
# 檢查環境變數
echo $HTTP_API_KEY

# 確認請求 header
curl -v -H "Authorization: Bearer your_key" http://localhost:8080/api/tools/list
```

---

### 問題：Connection Refused

**原因：** 伺服器未運行或網路問題

**解決：**
```bash
# 檢查伺服器狀態
docker ps | grep shioaji-mcp

# 檢查 port
netstat -tuln | grep 8080

# 檢查防火牆
sudo ufw status
```

---

### 問題：Not connected to Shioaji API

**原因：** Shioaji 憑證未設定或錯誤

**解決：**
```bash
# 檢查環境變數
echo $SHIOAJI_API_KEY
echo $SHIOAJI_SECRET_KEY

# 檢查健康狀態
curl http://localhost:8080/health
```

---

## 進階配置

### 使用 systemd 管理服務

建立 `/etc/systemd/system/shioaji-mcp-http.service`：

```ini
[Unit]
Description=Shioaji MCP HTTP API Server
After=network.target tailscaled.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/shioaji-mcp
Environment="SHIOAJI_API_KEY=your_key"
Environment="SHIOAJI_SECRET_KEY=your_secret"
Environment="HTTP_API_KEY=your_http_key"
Environment="HTTP_LISTEN_HOST=0.0.0.0"
Environment="HTTP_LISTEN_PORT=8080"
ExecStart=/usr/local/bin/shioaji-mcp-http
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

啟用服務：
```bash
sudo systemctl daemon-reload
sudo systemctl enable shioaji-mcp-http
sudo systemctl start shioaji-mcp-http
sudo systemctl status shioaji-mcp-http
```

---

### 使用 Docker Compose

建立 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  shioaji-mcp-http:
    image: shioaji-mcp:latest
    container_name: shioaji-mcp-http
    restart: unless-stopped
    environment:
      - MCP_MODE=http
      - SHIOAJI_API_KEY=${SHIOAJI_API_KEY}
      - SHIOAJI_SECRET_KEY=${SHIOAJI_SECRET_KEY}
      - HTTP_API_KEY=${HTTP_API_KEY}
      - HTTP_LISTEN_HOST=0.0.0.0
      - HTTP_LISTEN_PORT=8080
      - SHIOAJI_TRADING_ENABLED=false
    ports:
      - "127.0.0.1:8080:8080"
    # 或使用 Tailscale IP
    # ports:
    #   - "${TAILSCALE_IP}:8080:8080"
```

啟動：
```bash
docker-compose up -d
```

---

## 授權與支援

本專案採用 MIT 授權。

如有問題或建議，請提交 GitHub Issue。

---

## 更新日誌

### v0.1.1 (2024-01-XX)
- ✅ 新增 HTTP API 模式
- ✅ 支援 API Key 驗證
- ✅ Docker multi-mode 支援
- ✅ 完整的 API 文件
