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
import html

# ============================================================
# API KEY LOADING
# Supports both local (.env) and Streamlit Cloud (secrets)
# ============================================================

# Load from .env file when running locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

def get_groq_api_key():
    """
    Load GROQ_API_KEY from:
    1. Streamlit Cloud secrets (for cloud deployment)
    2. Environment variable / .env file (for local development)
    """
    # Try Streamlit secrets first (Streamlit Cloud)
    try:
        return st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass

    # Fall back to environment variable (local .env)
    return os.getenv("GROQ_API_KEY", "")

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

# Import the travel agent (clean, modular import)
from agent import create_travel_agent

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Travel Agent 🌍",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS STYLING
# ============================================================

st.markdown("""
<style>
    .main { padding: 2rem; }

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

    .stButton>button:hover {
        background-color: #FF6B6B;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
    }

    .trip-output {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border-left: 4px solid #FF4B4B;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        margin: 1rem 0;
    }

    h1 { color: #FF4B4B; text-align: center; }

    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    .success-banner {
        background: linear-gradient(90deg, #00C853 0%, #64DD17 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }

    .warning-banner {
        background: linear-gradient(90deg, #FF9800 0%, #FFC107 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }

    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if 'result' not in st.session_state:
    st.session_state.result = None
if 'planning' not in st.session_state:
    st.session_state.planning = False
if 'no_flights' not in st.session_state:
    st.session_state.no_flights = False

# ============================================================
# HEADER SECTION
# ============================================================

st.title("🌍 AI Travel Agent")
st.markdown('<p class="subtitle">Plan your perfect one-way trip with AI assistance!</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================
# SIDEBAR - INPUT FORM
# ============================================================

with st.sidebar:
    st.header("✈️ Trip Planning")

    # API Key Configuration
    st.markdown("#### 🔑 API Configuration")
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        value=get_groq_api_key(),
        help="Enter your Groq API key from console.groq.com"
    )

    st.markdown("---")

    # Trip Details Section
    st.markdown("#### 📍 Trip Details")

    source_city = st.text_input(
        "From City",
        value="Delhi",
        placeholder="e.g., Delhi, Mumbai, Bangalore",
        help="Your departure city"
    )

    destination_city = st.text_input(
        "To City",
        value="Kolkata",
        placeholder="e.g., Kolkata, Goa, Jaipur",
        help="Your destination city"
    )

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

    max_hotel_price = st.slider(
        "Max Hotel Price (per night)",
        min_value=1000,
        max_value=10000,
        value=5000,
        step=500,
        help="Maximum price per night for hotel"
    )

    min_hotel_stars = st.select_slider(
        "Minimum Hotel Rating",
        options=[1, 2, 3, 4, 5],
        value=3,
        help="Minimum star rating for hotel"
    )

    st.markdown("---")

    plan_button = st.button("🚀 Plan My Trip", use_container_width=True)

    st.markdown("---")
    st.info("💡 **Note:** If flights aren't available, we'll suggest trains/buses.")
    st.markdown("---")
    st.caption("Built with ❤️ using LangChain & Streamlit")

# ============================================================
# API KEY VALIDATION
# ============================================================

if not groq_api_key:
    col1, col2, col3 = st.columns([1, 2, 1])
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
# ============================================================

@st.cache_resource
def get_agent(_api_key):
    """Initialize and cache the travel planning agent."""
    return create_travel_agent(_api_key)

# ============================================================
# TRIP PLANNING LOGIC
# ============================================================

if plan_button:
    st.session_state.planning = True
    st.session_state.no_flights = False

    if not source_city or not destination_city:
        st.error("❌ Please enter both source and destination cities")
        st.stop()

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

    with st.status("🔍 Planning Your Trip...", expanded=True) as status:
        st.write("🔎 Searching for flights...")
        try:
            agent_executor = get_agent(groq_api_key)
            st.write("🏨 Finding hotels...")
            st.write("📍 Discovering attractions...")
            st.write("🌤️ Checking weather & estimating budget...")

            response = agent_executor.invoke({"input": query})
            st.session_state.result = response["output"]

            if "No direct flights" in st.session_state.result or "No flights" in st.session_state.result:
                st.session_state.no_flights = True

            status.update(label="✅ Trip planned successfully!", state="complete", expanded=False)
            st.session_state.planning = False

        except Exception as e:
            status.update(label="❌ Planning failed", state="error", expanded=True)
            st.error(f"Error: {str(e)}")
            st.info("💡 Tip: Make sure your API key is valid and try again")
            st.session_state.planning = False
            st.stop()

# ============================================================
# RESULTS DISPLAY SECTION
# ============================================================

if st.session_state.result:
    if st.session_state.no_flights:
        st.markdown('<div class="warning-banner">⚠️ No flights available - Alternative transport suggested</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-banner">✅ Your trip has been planned successfully!</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Trip Plan", "📊 Quick View", "💾 Export"])

    with tab1:
        st.markdown("### Your Complete Travel Plan")
        if st.session_state.no_flights:
            st.warning("🚂 **Note:** Direct flights not available for this route. Consider booking train or bus tickets through IRCTC or RedBus.")
        # Use st.text() to correctly render plain text with newlines and special chars (₹, emojis, dashes)
        # Wrapping in a styled container via st.container
        with st.container():
            st.markdown("""
            <style>
            .output-box {
                background-color: #f8f9fa;
                padding: 1.5rem 2rem;
                border-radius: 10px;
                border-left: 4px solid #FF4B4B;
                font-family: 'Courier New', monospace;
                font-size: 0.95rem;
                line-height: 1.7;
                white-space: pre-wrap;
                word-break: break-word;
                margin: 1rem 0;
                color: #212529;
            }
            </style>
            """, unsafe_allow_html=True)
            # Escape HTML special chars before injecting into div
            safe_result = html.escape(st.session_state.result)
            st.markdown(f'<div class="output-box">{safe_result}</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("### 📊 Trip Summary")
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

        if "Total Cost:" in st.session_state.result:
            total_cost = st.session_state.result.split("Total Cost: ₹")[1].split("\n")[0]
            st.markdown(f"### 💰 Total Trip Cost: **₹{total_cost}**")

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

    with tab3:
        st.markdown("### 💾 Export Your Itinerary")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download as TXT",
                data=st.session_state.result,
                file_name=f"trip_{source_city}_to_{destination_city}_{trip_days}days.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="📄 Download as MD",
                data=st.session_state.result,
                file_name=f"trip_{source_city}_to_{destination_city}_{trip_days}days.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("### 📋 Copy to Clipboard")
        st.code(st.session_state.result, language=None)
        st.caption("Select the text above and copy (Ctrl+C / Cmd+C)")

        if st.session_state.no_flights:
            st.info("💡 **Reminder:** Don't forget to book your train/bus tickets separately!")

        st.success("💡 Save your itinerary and share it with your travel companions!")

else:
    col1, col2, col3 = st.columns([1, 3, 1])
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

        ---

        **Ready to explore?** Fill in the sidebar and click "Plan My Trip"! 🌍
        """)
