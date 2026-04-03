from typing import Literal

from google.adk import Agent
from google.adk import Context
from google.adk import Event
from google.adk import Workflow
from google.adk.workflow import node
from pydantic import BaseModel
from pydantic import Field


class Feedback(BaseModel):
  grade: Literal["tech-related", "unrelated"] = Field(
      description=(
          "Decide if the headline is related to technology or software"
          " engineering."
      ),
  )
  feedback: str = Field(
      description=(
          "If the headline is unrelated to technology, provide feedback on how"
          " to make it more tech-focused."
      ),
  )


generate_headline = Agent(
    name="generate_headline",
    instruction="""
    Write a headline about the topic "{topic}".
    If feedback is provided, take it into account.
    The feedback: {feedback?}
    """,
)


evaluate_headline = Agent(
    name="evaluate_headline",
    instruction="""
    Grade whether the headline is related to technology or software engineering.
    """,
    output_schema=Feedback,
    output_key="feedback",
    # TODO: Remove after auto mode.
    mode="single_turn",
)


@node(rerun_on_resume=True)
async def orchestrate(ctx: Context, node_input: str) -> str:
  yield Event(state={"topic": node_input})

  while True:
    headline = await ctx.run_node(generate_headline)
    # TODO: This doesn't work yet.
    feedback = Feedback.model_validate(
        await ctx.run_node(evaluate_headline, node_input=headline)
    )
    if feedback.grade == "tech-related":
      yield headline
      break


root_agent = Workflow(
    name="root_agent",
    edges=[("START", orchestrate)],
)