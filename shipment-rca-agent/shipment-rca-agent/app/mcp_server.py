"""Expose the same logistics tools over MCP so Claude Desktop / Claude Code can use them.
Run: python -m app.mcp_server"""
from mcp.server.fastmcp import FastMCP
from app import tools

mcp = FastMCP("logistics-tools")
mcp.tool()(tools.get_tracking_events)
mcp.tool()(tools.get_carrier_performance)
mcp.tool()(tools.check_pincode_serviceability)

if __name__ == "__main__":
    mcp.run()
