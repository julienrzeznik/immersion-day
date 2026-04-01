from google.adk.agents import Agent
from google.adk.code_executors import BuiltInCodeExecutor

coding_agent = Agent(
    model='gemini-2.5-flash',
    name='CodeAgent',
    description=(
        "Specialist in code execution. Use it for all arithmetic operations"
    ),
    instruction="""
    You're a specialist in Code Execution
    """,
    code_executor=BuiltInCodeExecutor(),
)
