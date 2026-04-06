from google.adk import Agent
from google.adk import Event
from google.adk import Workflow
from google.adk.workflow import DEFAULT_ROUTE
from pydantic import BaseModel
from pydantic import Field
import json
from a2ui.core.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog


class PatientIdentity(BaseModel):
  """Output schema for the intake agent."""

  name: str = Field(description="The patient's full name.")
  phone_number: str = Field(description="The patient's phone number.")


class AgentResponse(BaseModel):
  """Output schema for the generate instruction agent."""

  text_response: str = Field(description="The conversational text to show in the chat.")
  ui_payload: list[dict] = Field(description="The A2UI protocol messages (beginRendering, surfaceUpdate).")


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[
        BasicCatalog.get_config("0.8"),
    ],
)

intake_instruction = schema_manager.generate_system_prompt(
    role_description="You are a medical lab intake assistant.",
    workflow_description="Your job is to chat with the user to get their full name and phone number. Do not make up information. Once you have both, finish your task.",
    ui_description="Use Forms for user input when appropriate.",
    include_schema=True,
    include_examples=True,
)
intake_instruction = intake_instruction.replace("{expression}", "{expression?}")

intake_agent = Agent(
    name="intake_agent",
    mode="task",
    output_schema=PatientIdentity,
    instruction=intake_instruction,
)


def find_orders(node_input: PatientIdentity):
  """Mocks checking the database for the patient.

  Routes back to intake_agent if the name is not Jane Doe.
  Otherwise routes to success.
  """
  if node_input.name.lower() != "jane doe":
    ui_payload = """<a2ui-json>
{
  "beginRendering": {
    "surfaceId": "order_not_found_surface",
    "root": "root_card"
  }
}
</a2ui-json>
<a2ui-json>
{
  "surfaceUpdate": {
    "surfaceId": "order_not_found_surface",
    "components": [
      {
        "id": "root_card",
        "component": {
          "Card": {
            "child": "content_column"
          }
        }
      },
      {
        "id": "content_column",
        "component": {
          "Column": {
            "children": {
              "explicitList": [
                "title_text",
                "body_text"
              ]
            }
          }
        }
      },
      {
        "id": "title_text",
        "component": {
          "Text": {
            "text": {
              "literalString": "❌ Order Not Found"
            },
            "usageHint": "h4"
          }
        }
      },
      {
        "id": "body_text",
        "component": {
          "Text": {
            "text": {
              "literalString": "Could not find matching records for patient."
            },
            "usageHint": "body"
          }
        }
      }
    ]
  }
}
</a2ui-json>"""
    yield Event(
        message=f"Could not find matching records for {node_input.name}. Let's try again.\n{ui_payload}",
        route="retry",
    )
  else:
    yield Event(state={"orders": ["CBC (Complete Blood Count)", "Lipid Panel"], "validation_error": ""}, route=DEFAULT_ROUTE)


generate_instruction_prompt = schema_manager.generate_system_prompt(
    role_description="You are a medical lab assistant.",
    workflow_description="Based on the found orders, generate an A2UI interface with the orders and preparation instructions. The response MUST match the `AgentResponse` schema, with `text_response` for your chat message and `ui_payload` containing the A2UI protocol messages (`beginRendering`, `surfaceUpdate`).",
    ui_description="Use Card, Text, and List components.",
    include_schema=True,
    include_examples=True,
)
generate_instruction_prompt = generate_instruction_prompt.replace("{expression}", "{expression?}")
generate_instruction_prompt += "\nHere are the orders found in the database: {orders}\n"
generate_instruction_prompt += "\nPrevious validation error: {validation_error}\n"

generate_instruction = Agent(
    name="generate_instruction",
    mode="task",
    output_schema=AgentResponse,
    instruction=generate_instruction_prompt,
)


root_agent = Workflow(
    name="task_in_workflow",
    edges=[
        ("START", intake_agent, find_orders),
        (
            find_orders,
            {"retry": intake_agent, DEFAULT_ROUTE: generate_instruction},
        ),
    ],
)