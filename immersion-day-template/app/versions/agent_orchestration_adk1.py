from google.genai import types
from typing import Optional

from google.adk.agents import Agent, SequentialAgent
from google.adk.models import Gemini
from google.adk.tools.agent_tool import AgentTool

# NATIVE LLM INTEGRATIONS
from ..tools.native_llm_tools.google_search_native import google_search_agent
from ..tools.native_llm_tools.google_maps_native import google_maps_agent
from ..tools.native_llm_tools.code_execution import coding_agent

from google.adk.agents import Agent
from pydantic import BaseModel, Field

from ..tools.api_tools.openapi_no_auth import customers_toolset

class Customer(BaseModel):
    first_name: str = Field(description="The first name.")
    last_name: str = Field(description="The last name.")
    city: str = Field(description="The city of the customer.")
    restaurant: str = Field(description="A good restaurant in the city of the customer.")

class CustomerList(BaseModel):
    customers: list[Customer] = Field(description="The list of customers.")

customer_search_agent = Agent(
    model='gemini-2.5-flash',
    name='CustomerSearchAgent',
    instruction="""
    List the first 3 customers using the customers_toolset, and return the list of customers along with the city they live in
    """,
    tools=[customers_toolset],
    output_schema=CustomerList,
    output_key="customers"
)

restaurant_finder_agent = Agent(
    model='gemini-2.5-flash',
    name='RestaurantFinderAgent',
    instruction="""
    Use the google_maps_agent to find a good restaurant in the city of each customer {customers}.
    """,
    tools=[
        AgentTool(agent=google_maps_agent)
    ],
    output_schema=CustomerList,
    output_key="customers_with_restaurant"
)


formatter_agent = Agent(
    model='gemini-2.5-flash',
    name='FormatterAgent',
    instruction="""
    Format the list {customers_with_restaurant} in a markdown table
    """
)


market_research_agent = SequentialAgent(
    name="market_research_agent",
    sub_agents=[
        customer_search_agent,
        restaurant_finder_agent,
        formatter_agent
    ]
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    You are a Marketing expert. When asked to do a marketing analysis, call the market_research_agent
    """,
    sub_agents=[
        market_research_agent
    ],
)
