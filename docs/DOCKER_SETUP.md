# Docker 映像設置指南

## 🚀 公開 Docker 映像

你的 Shioaji MCP Docker 映像已經成功建置並推送到 GitHub Container Registry！

### 映像位置
```
ghcr.io/offbeat-studio/shioaji-mcp:latest
```

### 設置映像為公開可見

GitHub Container Registry 的映像默認為私有。要讓映像公開可訪問，請按照以下步驟操作：

1. **前往包管理頁面**
   - 訪問: https://github.com/users/musingfox/packages/container/shioaji-mcp/settings
   - 或者：GitHub 個人檔案 → Packages → 找到 `shioaji-mcp` → Settings

2. **更改可見性**
   - 在 "Danger Zone" 區域找到 "Change package visibility"
   - 點擊 "Change visibility"
   - 選擇 "Public"
   - 確認更改

### 使用公開映像

設置為公開後，任何人都可以使用：

```bash
# 拉取映像
docker pull ghcr.io/offbeat-studio/shioaji-mcp:latest

# 執行 MCP 服務器
docker run --rm -i \
  -e SHIOAJI_API_KEY=your_api_key \
  -e SHIOAJI_SECRET_KEY=your_secret_key \
  -e SHIOAJI_TRADING_ENABLED=false \
  ghcr.io/offbeat-studio/shioaji-mcp:latest
```

### 在 MCP 配置中使用

更新你的 `mcp_config.json`：

```json
{
  "mcpServers": {
    "shioaji": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", "--platform=linux/amd64",
        "-e", "SHIOAJI_API_KEY=your_api_key_here",
        "-e", "SHIOAJI_SECRET_KEY=your_secret_key_here",
        "-e", "SHIOAJI_TRADING_ENABLED=false",
        "ghcr.io/offbeat-studio/shioaji-mcp:latest"
      ]
    }
  }
}
```

### 可用標籤

- `latest` - 最新穩定版本（來自 master 分支）
- `dev` - 開發版本（master 分支推送）
- `sha-xxxxxxx` - 特定 commit 版本
- `vX.Y.Z` - 版本標籤（當創建 release 時）

### 自動化更新

CI/CD 流程會在以下情況自動建置新映像：
- 推送到 master 分支
- 創建版本標籤 (v*)
- 發布 GitHub Release

### 多平台支援

映像支援以下平台：
- `linux/amd64` - Intel/AMD 64-bit
- `linux/arm64` - ARM 64-bit (Apple Silicon, ARM servers)

Docker 會自動選擇適合你系統的架構版本。

## 🔧 故障排除

### 無法拉取映像
如果遇到 "denied" 錯誤，請確保：
1. 映像已設置為公開
2. 映像名稱和標籤正確
3. 網路連接正常

### 權限問題
如果遇到權限問題，請檢查：
1. Docker daemon 是否正在運行
2. 用戶是否有 Docker 執行權限
3. 防火牆設置

### macOS 相容性
在 macOS 上，特別是 Apple Silicon (M1/M2)，請確保使用 `--platform=linux/amd64` 標誌以獲得最佳相容性。