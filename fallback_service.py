from app.services.catalog_service import enrich_item


def home_fallback(data: dict) -> dict:
    budget = data["budget"]
    items = data["items"]
    allocation = budget * 0.88 / len(items)
    recs = []
    for item in items:
        qty = item["quantity"]
        category = item["category"]
        platform = "IKEA" if category.lower() in {"dining table", "storage", "chair"} else "Amazon"
        recs.append(enrich_item({
            "title": f"Budget-friendly {data['style']} {category}",
            "category": category,
            "estimated_price": round(allocation / qty, 2),
            "quantity": qty,
            "reason": f"Selected for a {data['style']} {data['room_type']} setup.",
            "platform": platform,
        }))
    total = round(sum(x["estimated_price"] * x["quantity"] for x in recs), 2)
    return {
        "planner_type": "home",
        "title": f"{data['room_type']} budget plan",
        "budget": budget,
        "estimated_total": total,
        "remaining_budget": round(budget - total, 2),
        "summary": "A practical starter plan generated from your room, style, quantities and budget.",
        "budget_breakdown": [
            {"category": x["category"], "amount": round(x["estimated_price"] * x["quantity"], 2)}
            for x in recs
        ],
        "recommendations": recs,
        "tips": [
            "Compare dimensions before buying.",
            "Keep a small contingency for delivery or installation.",
            "Verify current prices and availability on the marketplace.",
        ],
    }


def party_fallback(data: dict) -> dict:
    budget = data["budget"]
    allocations = [
        ("Catering", budget * .45, data["guests"], "Swiggy", f"{data['food_preference']} catering package"),
        ("Venue", budget * .25, 1, "OYO", f"{data['venue_preference']} event venue"),
        ("Decoration", budget * .15, 1, "Amazon", f"{data['event_type']} decoration package"),
        ("Entertainment", budget * .10, 1, "Amazon", f"{data['event_type']} entertainment setup"),
    ]
    recs = [
        enrich_item({
            "title": title, "category": cat, "estimated_price": round(amount / qty, 2),
            "quantity": qty, "reason": f"Budget allocation for {data['guests']} guests.",
            "platform": platform,
        })
        for cat, amount, qty, platform, title in allocations
    ]
    total = round(sum(x["estimated_price"] * x["quantity"] for x in recs), 2)
    return {
        "planner_type": "party",
        "title": f"{data['event_type']} party plan",
        "budget": budget,
        "estimated_total": total,
        "remaining_budget": round(budget - total, 2),
        "summary": f"A balanced starter plan for {data['guests']} guests in {data['city']}.",
        "budget_breakdown": [
            {"category": "Catering", "amount": round(budget*.45, 2)},
            {"category": "Venue", "amount": round(budget*.25, 2)},
            {"category": "Decoration", "amount": round(budget*.15, 2)},
            {"category": "Entertainment", "amount": round(budget*.10, 2)},
            {"category": "Contingency", "amount": round(budget*.05, 2)},
        ],
        "recommendations": recs,
        "tips": [
            "Confirm per-head catering rates before booking.",
            "Ask venues about taxes, cleaning and overtime.",
            "Keep the contingency for unexpected expenses.",
        ],
    }


def jewelry_fallback(data: dict) -> dict:
    pieces = [
        ("Statement earrings", "Earrings", .25),
        ("Minimal necklace", "Necklace", .35),
        ("Bracelet or bangle", "Bracelet", .18),
        ("Elegant ring", "Ring", .12),
    ]
    recs = [
        enrich_item({
            "title": f"{data['style']} {title}",
            "category": category,
            "estimated_price": round(data["budget"] * ratio, 2),
            "quantity": 1,
            "reason": f"Suggested for a {data['occasion']} occasion with {data['metal']} preference.",
            "platform": "Flipkart" if category in {"Earrings", "Bracelet"} else "Amazon",
        })
        for title, category, ratio in pieces
    ]
    total = round(sum(x["estimated_price"] for x in recs), 2)
    return {
        "planner_type": "jewelry",
        "title": f"{data['occasion']} jewelry plan",
        "budget": data["budget"],
        "estimated_total": total,
        "remaining_budget": round(data["budget"] - total, 2),
        "summary": "A coordinated jewelry capsule based on occasion, style, metal preference and optional outfit details.",
        "budget_breakdown": [{"category": x["category"], "amount": x["estimated_price"]} for x in recs],
        "recommendations": recs,
        "tips": [
            "Use the outfit image as a visual reference, not a guarantee of exact color matching.",
            "Check metal/plating details and return policy.",
            "Verify current marketplace prices before purchase.",
        ],
    }
