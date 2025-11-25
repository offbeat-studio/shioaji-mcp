# MCP 工具對比範例

這個文件展示標準模式和簡化模式的實際使用差異。

## 場景 1：查詢帳戶狀態和餘額

### 標準模式（2 次工具調用）

```json
// 第 1 次調用
{
  "tool": "get_account_info",
  "arguments": {}
}

// 第 2 次調用
{
  "tool": "get_account_balance",
  "arguments": {
    "account_type": "all"
  }
}
```

### 簡化模式（1 次工具調用）

```json
{
  "tool": "account_status",
  "arguments": {
    "account_type": "all",
    "include_positions": true,
    "include_balance": true
  }
}
```

**優勢**：減少 50% 的調用次數，一次獲取完整資訊

---

## 場景 2：搜尋股票並查詢報價

### 標準模式（2 次工具調用）

```json
// 第 1 次：搜尋台積電
{
  "tool": "search_contracts",
  "arguments": {
    "keyword": "台積電"
  }
}

// 第 2 次：獲取報價（假設找到代碼是 2330）
{
  "tool": "get_snapshots",
  "arguments": {
    "contracts": ["2330"]
  }
}
```

### 簡化模式（2 次工具調用，但更直覺）

```json
// 第 1 次：搜尋
{
  "tool": "market_query",
  "arguments": {
    "search": "台積電"
  }
}

// 第 2 次：獲取報價
{
  "tool": "market_query",
  "arguments": {
    "symbols": ["2330"]
  }
}
```

**優勢**：使用同一個工具，AI 只需記住一個工具名稱

---

## 場景 3：查詢歷史資料

### 標準模式（1 次工具調用）

```json
{
  "tool": "get_kbars",
  "arguments": {
    "contract": "2330",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

### 簡化模式（1 次工具調用）

```json
{
  "tool": "market_query",
  "arguments": {
    "symbol": "2330",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

**優勢**：參數名稱更直覺（symbol vs contract）

---

## 場景 4：下單操作

### 標準模式（可能需要 2-3 次調用）

```json
// 第 1 次：先查詢現有訂單
{
  "tool": "list_orders",
  "arguments": {}
}

// 第 2 次：下新單
{
  "tool": "place_order",
  "arguments": {
    "contract": "2330",
    "action": "Buy",
    "quantity": 1000,
    "price": 500.0
  }
}

// 第 3 次：如果要取消
{
  "tool": "cancel_order",
  "arguments": {
    "order_id": "abc123"
  }
}
```

### 簡化模式（統一用一個工具）

```json
// 查詢訂單
{
  "tool": "order_management",
  "arguments": {
    "action": "list"
  }
}

// 下單
{
  "tool": "order_management",
  "arguments": {
    "action": "place",
    "symbol": "2330",
    "side": "buy",
    "quantity": 1000,
    "price": 500.0
  }
}

// 取消訂單
{
  "tool": "order_management",
  "arguments": {
    "action": "cancel",
    "order_id": "abc123"
  }
}
```

**優勢**：統一的動作模式，AI 更容易理解

---

## 場景 5：一次查詢多支股票

### 標準模式

```json
{
  "tool": "get_snapshots",
  "arguments": {
    "contracts": ["2330", "2317", "2454", "3443", "2382"]
  }
}
```

### 簡化模式

```json
{
  "tool": "market_query",
  "arguments": {
    "symbols": ["2330", "2317", "2454", "3443", "2382"]
  }
}
```

**優勢**：參數名更貼近日常用語（symbols vs contracts）

---

## 真實對話範例

### 使用標準模式的對話

```
用戶：幫我查看台積電的最新報價

AI：我需要先搜尋合約代碼
     [調用 search_contracts(keyword="台積電")]

     找到了，代碼是 2330。現在獲取報價...
     [調用 get_snapshots(contracts=["2330"])]

     台積電（2330）當前價格是 $520...

分析：需要 2 次工具調用，AI 需要理解搜尋和報價是兩個不同的工具
```

### 使用簡化模式的對話

```
用戶：幫我查看台積電的最新報價

AI：讓我查詢台積電的資料
     [調用 market_query(search="台積電")]

     找到了，現在獲取即時報價
     [調用 market_query(symbols=["2330"])]

     台積電（2330）當前價格是 $520...

分析：同樣 2 次調用，但 AI 只需要知道一個 market_query 工具
```

---

## 複雜場景：監控持倉並決定是否加碼

### 標準模式

```
用戶：查看我的台積電持倉，如果虧損超過 5% 就加碼 1000 股

AI：
1. [get_account_info()] - 獲取帳戶資訊
2. [get_positions(account_type="stock")] - 查詢持倉
3. [get_snapshots(contracts=["2330"])] - 獲取當前價格
4. 計算損益...虧損 6%，需要加碼
5. [place_order(contract="2330", action="Buy", quantity=1000)]

總共 4 次工具調用，需要理解 4 個不同工具
```

### 簡化模式

```
用戶：查看我的台積電持倉，如果虧損超過 5% 就加碼 1000 股

AI：
1. [account_status(include_positions=true)] - 一次獲取帳戶和持倉
2. [market_query(symbols=["2330"])] - 獲取當前價格
3. 計算損益...虧損 6%，需要加碼
4. [order_management(action="place", symbol="2330", side="buy", quantity=1000)]

總共 3 次工具調用，只需要理解 3 個工具
```

**優勢**：
- 減少 25% 的工具調用
- 工具名稱更容易理解
- 減少 AI 出錯的可能性

---

## 效能對比總結

| 場景 | 標準模式調用次數 | 簡化模式調用次數 | 節省 |
|-----|----------------|----------------|------|
| 查詢帳戶狀態 | 2-3 | 1 | 50-66% |
| 搜尋並查詢 | 2 | 2 | 0%* |
| 查詢歷史 | 1 | 1 | 0%* |
| 訂單操作 | 1-3 | 1-3 | 0%* |
| 複雜監控場景 | 4 | 3 | 25% |

\* 雖然調用次數相同，但簡化模式的**認知負擔更低**，AI 更容易正確選擇工具

---

## 結論

簡化模式的主要優勢不僅是減少工具調用次數，更重要的是：

1. **降低 AI 的認知負擔** - 從 11 個工具減少到 4 個
2. **提高工具選擇準確度** - 功能分類更清晰
3. **更符合自然語言習慣** - 工具名稱和參數更直覺
4. **減少 context 佔用** - 工具描述總量減少 42%
5. **提升用戶體驗** - 更快得到正確結果

**建議**：對於 AI 助理整合（如 Claude Desktop），強烈建議使用簡化模式！
