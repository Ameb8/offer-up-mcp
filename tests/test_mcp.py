import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_stdio_discovery_and_validation():
    params = StdioServerParameters(command=sys.executable, args=["-m", "offerup_mcp.server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert [t.name for t in tools.tools] == ["search_offerup"]
            result = await session.call_tool("search_offerup", {"query": "bike"})
            assert result.isError
            assert "zipcode or both" in result.content[0].text
