from urllib.parse import quote_plus

PLATFORMS = {
    "Amazon": "https://www.amazon.in/s?k={q}",
    "Flipkart": "https://www.flipkart.com/search?q={q}",
    "IKEA": "https://www.ikea.com/in/en/search/?q={q}",
    "Swiggy": "https://www.swiggy.com/search?query={q}",
    "Zomato": "https://www.zomato.com/chennai/restaurants?query={q}",
    "OYO": "https://www.oyorooms.com/search?location={q}",
}


def marketplace_url(platform: str, query: str) -> str:
    return PLATFORMS.get(platform, PLATFORMS["Amazon"]).format(q=quote_plus(query))


def enrich_item(item: dict) -> dict:
    platform = item.get("platform") or "Amazon"
    title = item.get("title") or "Recommended item"
    item["platform"] = platform
    item["search_url"] = marketplace_url(
        platform, f"{title} {item.get('category', '')}".strip()
    )
    item["estimated_price"] = float(item.get("estimated_price", 0) or 0)
    item["quantity"] = int(item.get("quantity", 1) or 1)
    return item
