---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description
A clear and concise description of what the bug is.

## Environment
- **OS**: [e.g. Ubuntu 22.04, macOS 13.0]
- **Docker version**: [e.g. 24.0.5]
- **Shioaji MCP version**: [e.g. latest, v0.1.0, dev]
- **MCP client**: [e.g. Claude, GPT-4, custom implementation]

## Reproduction Steps
Steps to reproduce the behavior:
1. Pull image '...'
2. Run command '....'
3. Configure MCP client '....'
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
What actually happened, including any error messages, logs, or screenshots.

## Docker Run Command
The command you used to run the Docker container (with sensitive information redacted):

```bash
docker run --rm -i --platform=linux/amd64 -e SHIOAJI_API_KEY=REDACTED -e SHIOAJI_SECRET_KEY=REDACTED ghcr.io/username/shioaji-mcp:tag
```

## MCP Client Configuration
Your MCP client configuration (with sensitive information redacted):

```json
{
  "mcpServers": {
    "shioaji": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", "--platform=linux/amd64",
        "-e", "SHIOAJI_API_KEY=REDACTED",
        "-e", "SHIOAJI_SECRET_KEY=REDACTED",
        "ghcr.io/username/shioaji-mcp:tag"
      ]
    }
  }
}
```

## Additional Context
Add any other context about the problem here, such as:
- Were you able to use the MCP server successfully before?
- Did this issue start after an update?
- Are you using any special Docker configurations?
