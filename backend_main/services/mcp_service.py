# import asyncio
# from langchain_mcp_adapters.client import MultiServerMCPClient

# mcp_client = MultiServerMCPClient({
#     "weather": {
#         "transport": "streamable_http",
#         "url": "http://127.0.0.1:8001/mcp",
#     }
# })


# def load_mcp_tools_sync():
#     """Load MCP tools once at import time. Falls back to an empty list
#     if the MCP server isn't reachable, so a dead weather server doesn't
#     take down disease/scheme retrieval too."""
#     try:
#         return asyncio.run(mcp_client.get_tools())
#     except Exception as e:
#         print(f"MCP weather server unreachable, skipping: {e}")
#         return []