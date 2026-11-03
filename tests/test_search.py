import json
import httpx
import pytest
from offerup_mcp.server import search, parse_page, SearchError


def page(lat=47.61, lon=-122.33):
    item = {"listingId": "abc", "title": "Bike", "price": "100", "locationName": "Seattle, WA"}
    data = {"props": {"pageProps": {"searchFeedParams": {"lat": str(lat), "lon": str(lon)},
            "searchFeedResponse": {"looseTiles": [{"listing": item}, {"tileType": "AD"}, {"listing": item}]}}}}
    return '<script type="application/json" id="__NEXT_DATA__">' + json.dumps(data) + '</script>'


def test_parser_filters_ads_duplicates_and_checks_area():
    result = parse_page(page(), 47.61, -122.33)
    assert result["count"] == 1
    assert result["listings"][0]["url"] == "https://offerup.com/item/detail/abc"
    with pytest.raises(SearchError, match="ignored"):
        parse_page(page(), 40, -70)
    with pytest.raises(SearchError, match="unexpected"):
        parse_page('<html>challenge</html>', 47.61, -122.33)


async def test_zip_search_passes_location_cookie():
    def handler(request):
        if request.url.host == "api.zippopotam.us":
            assert request.url.path == "/us/98101"
            return httpx.Response(200, json={"places": [{"latitude": "47.61", "longitude": "-122.33"}]})
        from urllib.parse import unquote
        loc = json.loads(unquote(request.headers["cookie"].split("=", 1)[1]))
        assert loc["latitude"] == 47.61
        assert request.url.params["q"] == "bicycle"
        assert request.url.params["radius"] == "10"
        return httpx.Response(200, text=page())
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await search("bicycle", zipcode="98101", radius_miles=10, client=client)
    assert result["count"] == 1


@pytest.mark.parametrize("kwargs", [{}, {"zipcode": "abcde"}, {"latitude": 91, "longitude": 0},
    {"zipcode": "98101", "latitude": 0}, {"latitude": 1, "longitude": 2, "radius_miles": 11}])
async def test_invalid_inputs(kwargs):
    with pytest.raises(SearchError):
        await search("bike", **kwargs)


async def test_rate_limit():
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(429))) as client:
        with pytest.raises(SearchError, match="rate-limited"):
            await search("bike", latitude=47.61, longitude=-122.33, client=client)
