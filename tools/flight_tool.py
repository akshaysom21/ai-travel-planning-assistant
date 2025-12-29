from langchain.tools import tool
from utils.load_json import load_json
from datetime import datetime
from tools.shared_state import store_selection

@tool
def search_flights(source: str, destination: str):
    """
    Search and select the cheapest one-way flight between two cities.
    If no flights available, suggests alternative transportation.

    Args:
        source: Departure city
        destination: Arrival city

    Returns:
        Flight details with pricing or alternative transport suggestion
    """
    try:
        flights = load_json("data/flights.json")

        # Filter flights (source → destination)
        options = [
            f for f in flights
            if f["from"].lower() == source.lower()
            and f["to"].lower() == destination.lower()
        ]

        if not options:
            # No flights found - suggest alternatives
            store_selection('flight_price', 0)
            store_selection('transport_mode', 'alternative')

            return f"""
❌ No flights available from {source} to {destination}

🚗 Alternative Transportation Options:
- Train - Comfortable and scenic (Recommended)
- Bus - Budget-friendly option
- Car Rental - Flexible travel
- Private Cab - Door-to-door service

💡 Suggestion: Consider booking train tickets through IRCTC or check bus services like RedBus.

Note: Trip planning will continue with hotel and attraction recommendations.
"""

        # Select the cheapest flight
        cheapest = min(options, key=lambda x: x["price"])

        # Format times
        dep_time = datetime.fromisoformat(cheapest["departure_time"]).strftime("%H:%M")
        arr_time = datetime.fromisoformat(cheapest["arrival_time"]).strftime("%H:%M")

        # Store flight details for budget calculation
        store_selection('flight_price', cheapest['price'])
        store_selection('airline', cheapest['airline'])
        store_selection('departure_time', dep_time)
        store_selection('transport_mode', 'flight')

        return f"""
Flight: {cheapest['airline']} (₹{cheapest['price']}) – Departs {source} at {dep_time}, Arrives at {arr_time}
Reason: Cheapest available option
"""

    except FileNotFoundError:
        return "❌ Error: flights.json file not found."
    except Exception as e:
        return f"❌ Error searching flights: {str(e)}"
