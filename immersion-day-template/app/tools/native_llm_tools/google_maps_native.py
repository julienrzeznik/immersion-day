from google.adk.agents import Agent

from google.adk.tools import google_maps_grounding

google_maps_agent = Agent(
    model='gemini-2.5-flash',
    name='GoogleMapsAgent',
    description=(
        "Uses Google Maps to find information"
    ),
    instruction="""
    You're a specialist in Google Maps
    """,
    tools=[google_maps_grounding],
)
