"""
Shared state for storing travel selections across tools
"""

travel_selections = {}

def store_selection(key, value):
    """Store a selection value"""
    travel_selections[key] = value

def get_selection(key, default=None):
    """Retrieve a selection value"""
    return travel_selections.get(key, default)

def clear_selections():
    """Clear all selections (useful for new queries)"""
    travel_selections.clear()
