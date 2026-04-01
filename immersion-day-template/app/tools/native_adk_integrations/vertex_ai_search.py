from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool
from google.adk.tools import agent_tool

from app.config import VERTEX_AI_SEARCH_DATASTORE

rag_agent = Agent(
 name='rag_agent',
 model='gemini-2.5-flash',
 description=(
     'Agent specialized in performing searches.'
 ),
 instruction='Use the VertexAISearchTool to find information.',
 tools=[
   VertexAiSearchTool(
     data_store_id=VERTEX_AI_SEARCH_DATASTORE
   )
 ],
)


rag_tool = agent_tool.AgentTool(agent=rag_agent)

