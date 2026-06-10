from pathlib import Path
from fastmcp import FastMCP
from fastmcp.server.providers import FileSystemProvider


mcp = FastMCP("job-search-server")
mcp.add_provider(FileSystemProvider(
    root=Path(__file__).parent / "components", reload=True)
)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8000)
