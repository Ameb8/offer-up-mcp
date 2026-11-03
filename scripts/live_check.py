"""Verify free search via the same stdio tool interface an agent uses."""
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    async with stdio_client(StdioServerParameters(command=sys.executable, args=["-m", "offerup_mcp.server"])) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            use_zip = "--zip" in sys.argv
            result = await session.call_tool("search_offerup", {
                "query": "bicycle",
                **({"zipcode": "98101"} if use_zip else {"latitude": 47.6101, "longitude": -122.3344}),
                "radius_miles": 10, "limit": 5,
            })
            if result.isError:
                raise RuntimeError(result.content)
            data = result.structuredContent or json.loads(result.content[0].text)
            assert data["count"] > 0, data
            assert 47.5 < data["area"]["latitude"] < 47.8
            assert -122.5 < data["area"]["longitude"] < -122.2
            for item in data["listings"]:
                assert item["url"].startswith("https://offerup.com/item/detail/")
                print(item["title"], "|", item["price"], "|", item["location"])
            print("Live MCP search passed:", data["count"], "listings")


asyncio.run(main())
