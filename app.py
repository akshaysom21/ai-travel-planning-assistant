# ============================================================
# AI Travel Planning Assistant - Streamlit Application
# 
# Purpose: User-friendly web interface for AI-powered travel planning
# 
# Features:
# - Interactive trip planning with customizable parameters
# - Real-time itinerary generation using LangChain agents
# - Support for flights, trains, and buses
# - Weather forecasts and budget estimates
# - Export functionality for trip plans
# 
# Author: AKSHAY SOM
# ============================================================

import streamlit as st
import os
import sys
import time

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

# Import the travel agent (clean, modular import)
from agent import create_travel_agent

# ============================================================
# PAGE CONFIGURATION
# Set up the Streamlit page with custom settings
# ============================================================

st.set_page_config(
    page_title="AI Travel Agent 🌍",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS STYLING
# Enhance the UI with custom styles for better user experience
# ============================================================

st.markdown("""
<style>
    /* Main container padding */
    .main {
        padding: 2rem;
    }
    
    /* Primary button styling */
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        font-size: 18px;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        width: 100%;
        transition: all 0.3s;
    }
    
    /* Button hover effect */
    .stButton>button:hover {
        background-color: #FF6B6B;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
    }
    
    /* Trip output display area */
    .trip-output {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border-left: 4px solid #FF4B4B;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        margin: 1rem 0;
    }
    
    /* Main title styling */
    h1 {
        color: #FF4B4B;
        text-align: center;
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Success banner */
    .success-banner {
        background: linear-gradient(90deg, #00C853 0%, #64DD17 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    /* Warning banner */
    .warning-banner {
        background: linear-gradient(90deg, #FF9800 0%, #FFC107 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    /* Info card styling */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Sidebar input fields */
    .sidebar .stTextInput > div > div > input {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# Store application state across reruns
# ============================================================

if 'result' not in st.session_state:
    st.session_state.result = None
if 'planning' not in st.session_state:
    st.session_state.planning = False
if 'no_flights' not in st.session_state:
    st.session_state.no_flights = False

# ============================================================
# HEADER SECTION
# Display main title and subtitle
# ============================================================

st.title("🌍 AI Travel Agent")
st.markdown('<p class="subtitle">Plan your perfect one-way trip with AI assistance!</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================
# SIDEBAR - INPUT FORM
# Collect all trip parameters from user
# ============================================================

with st.sidebar:
    st.header("✈️ Trip Planning")

    # API Key Configuration
    st.markdown("#### 🔑 API Configuration")
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        value=os.getenv("GROQ_API_KEY", ""),
        help="Enter your Groq API key from console.groq.com"
    )

    st.markdown("---")
    
    # Trip Details Section
    st.markdown("#### 📍 Trip Details")

    # Source city input
    source_city = st.text_input(
        "From City",
        value="Delhi",
        placeholder="e.g., Delhi, Mumbai, Bangalore",
        help="Your departure city"
    )

    # Destination city input
    destination_city = st.text_input(
        "To City",
        value="Kolkata",
        placeholder="e.g., Kolkata, Goa, Jaipur",
        help="Your destination city"
    )

    # Trip duration selector
    trip_days = st.number_input(
        "Trip Duration (days)",
        min_value=1,
        max_value=14,
        value=3,
        help="Number of days for your trip"
    )

    st.markdown("---")
    
    # Hotel Preferences Section
    st.markdown("#### 🏨 Preferences")

    # Hotel budget slider
    max_hotel_price = st.slider(
        "Max Hotel Price (per night)",
        min_value=1000,
        max_value=10000,
        value=5000,
        step=500,
        help="Maximum price per night for hotel"
    )

    # Hotel rating selector
    min_hotel_stars = st.select_slider(
        "Minimum Hotel Rating",
        options=[1, 2, 3, 4, 5],
        value=3,
        help="Minimum star rating for hotel"
    )

    st.markdown("---")

    # Plan Trip Button
    plan_button = st.button("🚀 Plan My Trip", use_container_width=True)

    # Additional Information
    st.markdown("---")
    st.info("💡 **Note:** If flights aren't available, we'll suggest trains/buses.")
    st.markdown("---")
    st.caption("Built with ❤️ using LangChain & Streamlit")

# ============================================================
# API KEY VALIDATION
# Check if API key is provided before proceeding
# ============================================================

if not groq_api_key:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.warning("⚠️ Please enter your Groq API key in the sidebar")
        st.info("💡 Get a free API key from [Groq Cloud](https://console.groq.com)")

        st.markdown("### 🎯 How to Get Started:")
        st.markdown("""
        1. Sign up at [console.groq.com](https://console.groq.com)
        2. Generate your API key
        3. Paste it in the sidebar
        4. Fill in trip details
        5. Click "Plan My Trip"
        """)
    st.stop()

# ============================================================
# AGENT INITIALIZATION WITH CACHING
# Cache the agent to avoid recreating it on every interaction
# ============================================================

@st.cache_resource
def get_agent(_api_key):
    """
    Initialize and cache the travel planning agent.
    
    Args:
        _api_key (str): Groq API key (underscore prefix prevents hashing)
    
    Returns:
        AgentExecutor: Configured travel planning agent
    """
    return create_travel_agent(_api_key)

# ============================================================
# TRIP PLANNING LOGIC
# Handle the trip planning process when button is clicked
# ============================================================

if plan_button:
    # Set planning state
    st.session_state.planning = True
    st.session_state.no_flights = False

    # Validate user inputs
    if not source_city or not destination_city:
        st.error("❌ Please enter both source and destination cities")
        st.stop()

    # Build comprehensive query for the agent
    query = f"""
    Plan a {trip_days} day one-way trip from {source_city} to {destination_city}.
    
    Hotel Requirements:
    - Maximum price: ₹{max_hotel_price} per night
    - Minimum rating: {min_hotel_stars} stars

    CRITICAL REQUIREMENTS:
    - Generate a COMPLETE {trip_days}-day itinerary
    - Show activities for ALL {trip_days} days: Day 1, Day 2, Day 3, ... up to Day {trip_days}
    - Include 2-3 places/activities per day
    - Provide weather forecast for all {trip_days} days
    - Last day should include checkout and departure activities

    IMPORTANT: Do NOT skip any days. Every single day from 1 to {trip_days} MUST appear in the itinerary section.
    """

    # Show planning progress with animated status
    progress_placeholder = st.empty()
    with progress_placeholder.container():
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Planning Your Trip...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Step 1: Searching flights
        status_text.text("🔎 Searching for flights...")
        progress_bar.progress(20)

    try:
        # Initialize the agent with API key
        agent_executor = get_agent(groq_api_key)

        # Step 2: Finding hotels
        status_text.text("🏨 Finding hotels...")
        progress_bar.progress(40)

        # Step 3: Discovering attractions
        status_text.text("📍 Discovering attractions...")
        progress_bar.progress(60)

        # Step 4: Checking weather
        status_text.text("🌤️ Checking weather...")
        progress_bar.progress(80)

        # Execute the agent with the query
        response = agent_executor.invoke({"input": query})
        st.session_state.result = response["output"]

        # Check if flights were unavailable
        if "No direct flights" in st.session_state.result or "No flights" in st.session_state.result:
            st.session_state.no_flights = True

        # Step 5: Completed
        progress_bar.progress(100)
        status_text.text("✅ Trip planned successfully!")

        st.markdown('</div>', unsafe_allow_html=True)
        st.session_state.planning = False

        # Clear progress indicator after brief delay
        time.sleep(1)
        progress_placeholder.empty()

    except Exception as e:
        # Handle errors gracefully
        progress_placeholder.empty()
        st.error(f"❌ Error planning trip: {str(e)}")
        st.info("💡 Tip: Make sure your API key is valid and try again")
        st.session_state.planning = False
        st.stop()

# ============================================================
# RESULTS DISPLAY SECTION
# Show the generated itinerary if available
# ============================================================

if st.session_state.result:
    # Display appropriate status banner
    if st.session_state.no_flights:
        st.markdown('<div class="warning-banner">⚠️ No flights available - Alternative transport suggested</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-banner">✅ Your trip has been planned successfully!</div>', unsafe_allow_html=True)

    # Create tabbed interface for results
    tab1, tab2, tab3 = st.tabs(["📋 Trip Plan", "📊 Quick View", "💾 Export"])

    # ============================================================
    # TAB 1: COMPLETE TRIP PLAN
    # ============================================================
    with tab1:
        st.markdown("### Your Complete Travel Plan")

        # Show warning for alternative transport
        if st.session_state.no_flights:
            st.warning("🚂 **Note:** Direct flights not available for this route. Consider booking train or bus tickets through IRCTC or RedBus.")

        # Display the formatted itinerary
        st.markdown(f'<div class="trip-output">{st.session_state.result}</div>', unsafe_allow_html=True)

    # ============================================================
    # TAB 2: QUICK SUMMARY VIEW
    # ============================================================
    with tab2:
        st.markdown("### 📊 Trip Summary")

        # Display key metrics in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🛫 From", source_city)
            st.metric("📅 Duration", f"{trip_days} days")

        with col2:
            st.metric("🛬 To", destination_city)
            st.metric("💰 Max Hotel", f"₹{max_hotel_price}")

        with col3:
            transport_mode = "Train/Bus" if st.session_state.no_flights else "Flight"
            st.metric("🚆 Transport", transport_mode)
            st.metric("⭐ Min Rating", f"{min_hotel_stars} stars")

        st.markdown("---")

        # Extract and display total cost
        if "Total Cost:" in st.session_state.result:
            total_cost = st.session_state.result.split("Total Cost: ₹")[1].split("\n")[0]
            st.markdown(f"### 💰 Total Trip Cost: **₹{total_cost}**")

        # Show booking links for alternative transport
        if st.session_state.no_flights:
            st.markdown("---")
            st.markdown("### 🚂 Book Alternative Transport:")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("🚆 **Train Tickets**")
                st.markdown("[Book on IRCTC →](https://www.irctc.co.in)")
            with col2:
                st.markdown("🚌 **Bus Tickets**")
                st.markdown("[Book on RedBus →](https://www.redbus.in)")

        st.info("💡 **Pro Tip:** Check the 'Trip Plan' tab for complete details including weather and daily itinerary")

    # ============================================================
    # TAB 3: EXPORT OPTIONS
    # ============================================================
    with tab3:
        st.markdown("### 💾 Export Your Itinerary")

        col1, col2 = st.columns(2)

        with col1:
            # Download as text file
            st.download_button(
                label="📥 Download as TXT",
                data=st.session_state.result,
                file_name=f"trip_{source_city}_to_{destination_city}_{trip_days}days.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:
            # Download as markdown file
            st.download_button(
                label="📄 Download as MD",
                data=st.session_state.result,
                file_name=f"trip_{source_city}_to_{destination_city}_{trip_days}days.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.markdown("---")
        
        # Copy to clipboard section
        st.markdown("### 📋 Copy to Clipboard")
        st.code(st.session_state.result, language=None)
        st.caption("Select the text above and copy (Ctrl+C / Cmd+C)")

        st.markdown("---")

        # Show reminder for alternative transport booking
        if st.session_state.no_flights:
            st.info("💡 **Reminder:** Don't forget to book your train/bus tickets separately!")

        st.success("💡 Save your itinerary and share it with your travel companions!")

else:
    # ============================================================
    # WELCOME SCREEN
    # Display when no trip has been planned yet
    # ============================================================
    
    col1, col2, col3 = st.columns([1,3,1])

    with col2:
        st.markdown("""
        ## 👋 Welcome to AI Travel Agent!

        **Plan your perfect trip in seconds with AI**

        ### 🚀 Getting Started:

        1. **Enter API Key** 🔑 - Add your Groq API key in the sidebar
        2. **Set Destination** 📍 - Choose where you want to go
        3. **Pick Duration** 📅 - Select trip length (1-14 days)
        4. **Set Preferences** 💰 - Choose hotel budget and rating
        5. **Click Plan** 🎯 - Let AI create your itinerary!

        ### ✨ What You'll Get:

        - ✈️ **Best Flight** - Or train/bus if flights unavailable
        - 🏨 **Perfect Hotel** - Matches your budget & preferences
        - 📍 **Top Attractions** - Must-visit places
        - 🌤️ **Weather Forecast** - Know what to pack
        - 💰 **Complete Budget** - Accurate cost breakdown
        - 📅 **Day-wise Plan** - Organized itinerary

        ### 🎯 Try These Popular Routes:

        - Delhi → Kolkata (3 days) - Culture & cuisine
        - Mumbai → Goa (4 days) - Beaches & nightlife
        - Bangalore → Chennai (3 days) - Tech & temples
        - Delhi → Jaipur (2 days) - Royal heritage

        ### 🚂 Smart Transport Options:

        If flights aren't available for your route, we'll suggest:
        - 🚆 Train connections (IRCTC)
        - 🚌 Bus services (RedBus)
        - 🚗 Car rental options

        ---

        **Ready to explore?** Fill in the sidebar and click "Plan My Trip"! 🌍
        """)

        # Sample output preview in expandable section
        with st.expander("👀 See Sample Output"):
            st.code("""
Your 3-Day Trip to Goa

Flight Selected:
- No direct flights available. Consider train/bus (estimated ₹2000)

Hotel Booked:
- Royal Heritage (₹1232/night, 5-star)

Weather:
- Day 1: Sunny (31°C)
- Day 2: Clear (30°C)
- Day 3: Partly Cloudy (29°C)

Itinerary:
Day 1: Beach relaxation, Fort visit
Day 2: Water sports, Local markets
Day 3: Heritage walk, Departure

Estimated Total Budget:
- Transport (Train/Bus - estimated): ₹2000
- Hotel: ₹3696
- Food & Travel: ₹4500
-------------------------------------
Total Cost: ₹10196

Note: Please book train/bus tickets separately via IRCTC/RedBus
            """, language=None)

# ============================================================
# FOOTER
# Display credits and version information
# ============================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p style='font-size: 0.9rem;'>Powered by <strong>LangChain</strong>, <strong>Groq AI</strong>, and <strong>Streamlit</strong></p>
    <p style='font-size: 0.8rem;'>🌟 AI Travel Agent v1.0 | Built with ❤️ for travelers</p>
    <p style='font-size: 0.8rem;'>© 2024 | Supports flights, trains & buses</p>
</div>
""", unsafe_allow_html=True)
