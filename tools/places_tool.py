from langchain.tools import tool
from utils.load_json import load_json

@tool
def discover_places(city: str, top_k: int = 5):
    """
    Discover top tourist attractions in a city.
    """
    places = load_json("data/places.json")

    filtered = [
        p for p in places
        if p["city"].lower() == city.lower()
    ]

    if not filtered:
        return f"No tourist attractions found in {city}."

    ranked = sorted(filtered, key=lambda x: x.get("rating", 0), reverse=True)[:top_k]

    formatted_places = "\n".join(
        f"- {p['name']} ({p.get('rating', 'N/A')}⭐): {p.get('category', 'Attraction')}"
        for p in ranked
    )

    return f"""
Top Tourist Attractions in {city}: {formatted_places}

Reason: Selected the highest-rated attractions to maximize sightseeing quality and traveler satisfaction.
"""
