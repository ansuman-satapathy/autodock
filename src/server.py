from mcp.server.fastmcp import FastMCP

# Initialize the AutoDock Server
mcp = FastMCP("AutoDock")

@mcp.tool()
def ping() -> str:
    """
    Basic connectivity check to ensure AutoDock is running.
    """
    return "Pong! AutoDock is online and ready for tools."

if __name__ == "__main__":
    mcp.run()
