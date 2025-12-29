from langchain.tools import tool
from utils.load_json import load_json
from tools.shared_state import store_selection

@tool
def recommend_hotel(city: str, max_price: int = 5000, min_stars: int = 3):
    """
    Recommend the best hotel based on rating and price.
    """
    try:
        hotels = load_json("data/hotels.json")

        filtered = [
            h for h in hotels
            if h["city"].lower() == city.lower()
            and h["price_per_night"] <= max_price
            and h["stars"] >= min_stars
        ]

        if not filtered:
            return f"❌ No hotels found in {city} matching criteria."

        best = sorted(filtered, key=lambda x: (-x["stars"], x["price_per_night"]))[0]

        store_selection('hotel_price_per_night', best['price_per_night'])
        store_selection('hotel_name', best.get('name', 'Selected Hotel'))

        amenities_str = ", ".join(best.get("amenities", [])) if best.get("amenities") else "Standard amenities"

        return f"""
🏨 Hotel Recommended

Name: {best.get('name', 'N/A')}
City: {city}
Rating: {best['stars']} ⭐
Price per Night: ₹{best['price_per_night']}
Amenities: {amenities_str}

Reason: Selected as the highest-rated hotel ({best['stars']} stars) within your budget.
"""

    except Exception as e:
        return f"❌ Error recommending hotel: {str(e)}"
