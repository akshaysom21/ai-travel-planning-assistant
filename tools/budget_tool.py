from langchain.tools import tool
from tools.shared_state import get_selection

@tool
def estimate_budget(days: int):
    """
    Estimate total travel budget for one-way trip.
    Handles cases where no flight is available.
    """
    try:
        flight_price = get_selection('flight_price', 0)
        hotel_price_per_night = get_selection('hotel_price_per_night', 2000)
        transport_mode = get_selection('transport_mode', 'flight')

        hotel_cost = hotel_price_per_night * days
        food_and_travel = 1500 * days

        # If no flight, estimate alternative transport cost
        if flight_price == 0 or transport_mode == 'alternative':
            estimated_transport = 2000  # Estimated train/bus cost
            total = estimated_transport + hotel_cost + food_and_travel

            return f"""
Budget (Flight not available - using estimated transport cost):
- Transport (Train/Bus - estimated): ₹{estimated_transport}
- Hotel: ₹{hotel_cost}
- Food & Travel: ₹{food_and_travel}
- Total: ₹{total}

Note: Transport cost is estimated. Please book train/bus separately and adjust budget accordingly.
"""
        else:
            # Normal flight budget
            total = flight_price + hotel_cost + food_and_travel

            return f"""
Budget:
- Flight: ₹{flight_price}
- Hotel: ₹{hotel_cost}
- Food & Travel: ₹{food_and_travel}
- Total: ₹{total}
"""

    except Exception as e:
        return f"Error: {str(e)}"
