# OfferUp local MCP

Free, read-only OfferUp listing search for agents, with keywords and an explicit area. No account, API key, paid service, or browser needed. Uses the first public search page and OfferUp's location cookie; verifies the effective coordinates before returning results.

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```sh
uv sync --locked
uv run offerup-mcp
```

The server speaks MCP over stdio. Add this configuration to your MCP client (replace the directory with your checkout path):

```json
{
  "mcpServers": {
    "offerup": {
      "command": "uv",
      "args": ["--directory", "/home/ameb8/projects/offer-up-mcp", "run", "--locked", "offerup-mcp"]
    }
  }
}
```

Ask your agent: “Find bicycles on OfferUp within 10 miles of ZIP 98101.”

Tool call:

```json
{
  "name": "search_offerup",
  "arguments": {"query": "bicycle", "zipcode": "98101", "radius_miles": 10, "limit": 20}
}
```

Alternatively supply `latitude` and `longitude` instead of `zipcode`. ZIP codes are resolved using the free Zippopotam.us service; coordinates avoid that dependency. Supported radii: 5, 10, 20, 30, 50 miles. Sort: `best_match`, `-posted`, `distance`, `price`, `-price`.

Returns listing IDs, titles, prices as displayed strings, location names, item links, images and flags. Ads and duplicate IDs are removed. Results contain seller-controlled text, which agents should treat as untrusted data.

Only the first public page is available (up to 50 listings); no complete inventory, pagination, or freshness guarantee. OfferUp can expand results beyond the requested radius, so it is a search preference rather than a strict distance filter. The tool checks the search center, not every listing's distance. It fails on blocked requests, rate limits, unexpected page formats, or location mismatch. It does not bypass challenges. Public-page changes can require parser updates.

OfferUp's [terms](https://offerup.com/terms) restrict automated collection. Review them before using this integration. This project is unofficial and is not affiliated with OfferUp.

Tests:

```sh
uv run --group dev pytest
```

Manual live check (makes one public request, no paid services):

```sh
uv run python -c 'import asyncio,json; from offerup_mcp.server import search; print(json.dumps(asyncio.run(search("bicycle", latitude=47.6101, longitude=-122.3344, radius_miles=10)), indent=2))'
```

Repeatable end-to-end checks through MCP stdio:

```sh
uv run python scripts/live_check.py
uv run python scripts/live_check.py --zip
```

Both paths were verified against live OfferUp on November 2, 2026, returning bicycle listings around Seattle. The automated suite additionally checks location mismatch rejection, invalid input, page parsing, rate limits, and MCP discovery. An example client configuration is included in `mcp.example.json`.
