# ============================================================================
# TRAVEL PLANNING AGENT
# ============================================================================
# Purpose: Orchestrate all tools to create comprehensive travel itineraries
# Architecture:
#   - Uses LangChain's create_openai_tools_agent
#   - Integrates Groq LLM for reasoning
#   - Combines multiple tools for complete planning
# Features:
#   - Natural language interaction
#   - Multi-step reasoning
#   - Context-aware decision making
# ============================================================================

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.flight_tool import search_flights
from tools.hotel_tool import recommend_hotel
from tools.places_tool import discover_places
from tools.weather_tool import get_weather
from tools.budget_tool import estimate_budget

def create_travel_agent(groq_api_key: str):
    """Create and configure the travel planning agent."""

    # Initialize Groq LLM with optimal settings
    llm = ChatGroq(
        api_key=groq_api_key,
        model="llama-3.1-8b-instant", # High-performance model
        temperature=0.3, # Low temperature for consistent results
        streaming=False
    )

    # Define agent prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         """
You Are an expert AI travel planner. Use tools to gather information and produce output in the EXACT format below.

WORKFLOW:
1. Use search_flights to find flight(if not available, note alternative transport)
2. Use recommend_hotel to find the best hotel
3. Use discover_places to get top 5-6 attractions
4. Use get_weather to get weather forecast for ALL trip days
5. Use estimate_budget to calculate total cost
6. Generate final output in format below

FINAL OUTPUT FORMAT:

Your [X]-Day Trip to [Destination]

Flight Selected:
- [If available: Airline (₹Price) – Departs Source at Time]
- [If NOT available: No direct flights available. Consider train/bus(estimated ₹2000)]

Hotel Booked:
- [Hotel Name] (₹ [Price]/night, [Stars] - star)

Weather:
- Day 1: [Condition] ([Temp]°C)
- Day 2: [Condition] ([Temp]°C)
[CONTINUE FOR EVERYDAY- if 5 days, show 5 days; if 7 days, show 7 days]

Itinerary:
Day 1: [Place 1], [Place 2]
Day 2: [Place 3], [Place 4]
[CONTINUE FOR EVERY DAY OF THE TRIP- DO NOT STOP AT DAY 3]
[If trip is 5 days: Day 1, Day 2, Day 3, Day 4, Day 5]
[If trip is 7 days: Day 1 through Day 7]
[Last day should include: Check-out, Departure]

Estimated Total Budget:
- [Flight or Transport]: ₹ [Amount]
- Hotel: ₹ [Amount]
- Food & Travel: ₹ [Amount]
-------------------------------------
Total Cost: ₹ [Total]

CRITICAL RULES:
- MUST show itinerary for EVERY SINGLE DAY from Day 1 to the last day
- Weather forecast must cover ALL days
- Distribute discovered places across all days(2 per day)
- If running out of specific places, suggest: "Local markets", "Leisure time", "City exploration"
- Last day always includes: checkout and departure
- Use ACTUAL data from tools
- Keep weather descriptions simple
- Use exact dashes (-----) before Total Cost
"""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    # Register available tools
    tools = [search_flights, recommend_hotel, discover_places, get_weather, estimate_budget]

    # Create the agent
    agent = create_openai_tools_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # Create agent executor
    agent_executor = (
        AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=8,
            early_stopping_method="force",
            return_intermediate_steps=False
        )
        .with_config({"stream": False})   # CRITICAL
    )

    return agent_executor
