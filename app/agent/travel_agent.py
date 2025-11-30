"""
Travel Agent - Core LangChain agent implementation
"""

from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from dotenv import load_dotenv

from app.tools.flight_search import search_flights
from app.tools.hotel_search import search_hotels
from app.tools.booking_tool import create_booking

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Define comprehensive system prompt
system_prompt = """You are an expert travel booking assistant with access to powerful tools for searching flights and hotels.

Your capabilities:
- Search for flights between any two cities with specific dates
- Find hotels in various locations with availability checking
- Create confirmed bookings for both flights and hotels

Guidelines for interaction:
1. Always be friendly, professional, and helpful
2. Ask clarifying questions if the user's request is ambiguous
3. Present options clearly with prices and key details
4. Confirm booking details before creating reservations
5. Use the available tools to provide real-time, accurate information
6. If you don't have enough information, politely ask the user for details

When searching for flights or hotels:
- Always extract the origin, destination, and dates from the user's message
- If dates are relative (like "next week"), calculate the actual dates
- Present multiple options when available
- Highlight the best value or recommended options

When creating bookings:
- Always confirm the details with the user first
- Ask for customer name and email before booking
- Provide clear confirmation with booking reference number
- Explain any important details about the booking

Remember: Your goal is to make travel booking as easy and pleasant as possible!"""

# Create prompt template with memory support
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Gather all tools
tools = [search_flights, search_hotels, create_booking]

# Create ReAct agent
agent = create_react_agent(llm, tools, prompt)

# Create agent executor with enhanced configuration
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10,
    early_stopping_method="generate"
)
