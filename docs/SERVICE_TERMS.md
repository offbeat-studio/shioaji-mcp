# 服務條款簽署功能

根據台灣金融法規，新用戶首次使用永豐金證券 API 需要完成服務條款簽署和 API 測試。

## 功能概述

### 1. 檢查簽署狀態 (`check_terms_status`)

檢查當前帳戶的服務條款簽署狀態和 API 測試完成情況。

**使用方式：**
```python
result = await handle_call_tool("check_terms_status", {})
```

**回傳資訊：**
- `account_id`: 帳戶 ID
- `broker_id`: 券商 ID  
- `account_type`: 帳戶類型（股票/期貨）
- `signed`: 是否已完成 API 測試（`True` 表示已完成）
- `username`: 使用者名稱

### 2. 執行 API 測試 (`run_api_test`)

在模擬環境中執行 API 測試，包含登入測試和下單測試。

**使用方式：**
```python
result = await handle_call_tool("run_api_test", {})
```

**測試項目：**
- 登入測試：驗證 API 金鑰是否有效
- 股票下單測試：使用 2890（永豐金）進行測試下單
- 期貨下單測試：使用台指期貨進行測試下單

## 重要注意事項

### 測試時間限制
- **可測試時間**：星期一至五 08:00 ~ 20:00
- **18:00 ~ 20:00**：只允許台灣 IP
- **08:00 ~ 18:00**：沒有 IP 限制

### 版本要求
- Shioaji 版本 >= 1.2
- 使用 API Key 進行登入（非身分證字號）

### 測試要求
- API 下單簽署時間須早於 API 測試時間
- 證券、期貨戶須各別測試
- 下單測試需間隔 1 秒以上
- 測試完成後等待約 5 分鐘審核

### 前置作業

1. **開戶**：必須先擁有[永豐金帳戶](https://www.sinotrade.com.tw/openact)

2. **簽署文件**：至[簽署中心](https://www.sinotrade.com.tw/newweb/Inside_Frame?URL=https://service.sinotrade.com.tw/signCenter/index/)簽署相關文件

3. **申請 API Key**：取得 API Key 和 Secret Key

## 使用範例

```python
import asyncio
from shioaji_mcp.tools.terms import check_terms_status, run_api_test

async def main():
    # 1. 檢查簽署狀態
    status = await check_terms_status({})
    print("簽署狀態:", status)
    
    # 2. 執行 API 測試（如果尚未完成）
    test_result = await run_api_test({})
    print("測試結果:", test_result)

asyncio.run(main())
```

## 狀態說明

- `signed=True`：恭喜完成測試！可以進行正式交易
- `signed=False` 或未顯示 `signed`：尚未通過 API 測試或尚未簽署文件

## 錯誤排除

1. **測試失敗**：確認是否在可測試時間內進行
2. **連線失敗**：檢查 API Key 和 Secret Key 是否正確
3. **IP 限制**：18:00-20:00 時段需使用台灣 IP
4. **版本問題**：確認 Shioaji 版本 >= 1.2

## MCP 配置範例

```json
{
  "mcpServers": {
    "shioaji": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", "--platform=linux/amd64",
        "-e", "SHIOAJI_API_KEY=your_api_key",
        "-e", "SHIOAJI_SECRET_KEY=your_secret_key",
        "shioaji-mcp"
      ]
    }
  }
}
```