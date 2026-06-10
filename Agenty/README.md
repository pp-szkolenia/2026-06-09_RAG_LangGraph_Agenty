# Serwer MCP + Agent AI


## Jak uruchomić

Terminal 1:

```bash
uv run mcp_server/main.py
```

Terminal 2:

Linux:
```bash
CLIENT_PORT=7000 SERVER_PORT=7001 npx @modelcontextprotocol/inspector
```

Windows (PowerShell):
```bash
$env:CLIENT_PORT="7000"; $env:SERVER_PORT="7001"; npx @modelcontextprotocol/inspector
```

W przeglądarce wejdź pod adres URL widoczny w terminalu 2:

```bash

http://localhost:7000/?MCP_PROXY_AUTH_TOKEN=xyz123....
```

- Jako Transport Type wybierz `Streamable HTTP`
- URL: `http://localhost:8000/mcp`
- Configuration -> Inspector Proxy Address -> `http://localhost:7001`
