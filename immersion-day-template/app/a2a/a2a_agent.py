import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field

# NATIVE LLM INTEGRATIONS
from ..tools.native_llm_tools.google_maps_native import google_maps_agent
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

# Expose the agent via A2A Protocol
# The client can communicate with it using the A2A inspector
a2a_app = to_a2a(market_research_agent, port=8001)

# Persistent URL Override Fix:
# We lazily build the agent card inside the async route handler to avoid module-level asyncio.run() issues.
from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder
from starlette.responses import JSONResponse
from starlette.routing import Route

_cached_card = None

async def corrected_card_handler(request):
    global _cached_card
    if _cached_card is None:
        # Build the card automatically using the actual base_url from the request
        builder = AgentCardBuilder(agent=market_research_agent, rpc_url=str(request.base_url))
        _cached_card = await builder.build()
        _cached_card.default_input_modes = ["text/plain", "application/json"]
        _cached_card.default_output_modes = ["text/plain", "application/json"]
        
    # Ensure the URL is always perfectly synced with the incoming request host
    url = str(request.base_url).rstrip("/")
    # Starlette often interprets Cloud Run TLS termination as HTTP without ProxyHeadersMiddleware.
    # Force HTTPS when deployed on Cloud Run to avoid 302 redirects which drop POST bodies.
    if "run.app" in url and url.startswith("http://"):
        url = url.replace("http://", "https://", 1)
        
    _cached_card.url = url
    return JSONResponse(_cached_card.model_dump(mode="json"))

a2a_app.router.routes.insert(0, Route("/.well-known/agent-card.json", endpoint=corrected_card_handler))

if __name__ == "__main__":
    import uvicorn
    # Standalone execution if run directly
    uvicorn.run("app.a2a.a2a_agent:a2a_app", host="localhost", port=8001, reload=True)
