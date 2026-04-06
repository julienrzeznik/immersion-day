import logging
import os
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import TaskState, TextPart, Part, AgentCard, AgentCapabilities
from a2a.utils import new_agent_parts_message, new_task
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.genai import types
from starlette.middleware.cors import CORSMiddleware
from agent import root_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowAgentExecutor(AgentExecutor):
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            app_name="a2ui_agent",
            agent=root_agent,
            session_service=self.session_service,
            artifact_service=InMemoryArtifactService(),
            memory_service=InMemoryMemoryService(),
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.get_user_input()
        logger.info(f"Executing workflow with query: {query}")

        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        
        from a2a.server.tasks import TaskUpdater
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        current_message = types.Content(
            role="user", parts=[types.Part.from_text(text=query)]
        )

        last_output = ""

        session_id = task.context_id or "default_session"
        session = await self.session_service.get_session(app_name="a2ui_agent", user_id="user", session_id=session_id)
        if not session:
            await self.session_service.create_session(app_name="a2ui_agent", user_id="user", session_id=session_id)

        async for event in self.runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=current_message,
        ):
            logger.info(f"Received event from runner: {event}")
            text = None
            content = getattr(event, 'content', None)
            if content and hasattr(content, 'parts') and content.parts:
                part = content.parts[0]
                text = getattr(part, 'text', None)
                
                # Handle function calls that contain AgentResponse
                if not text and hasattr(part, 'function_call') and part.function_call:
                    fc = part.function_call
                    args = fc.args
                    if args and isinstance(args, dict) and 'text_response' in args and 'ui_payload' in args:
                        text_response = args['text_response']
                        ui_payload = args['ui_payload']
                        text = f"{text_response}\n<a2ui-json>\n{json.dumps(ui_payload)}\n</a2ui-json>"
            
            if not text and hasattr(event, 'output') and event.output:
                if isinstance(event.output, str):
                    text = event.output
                else:
                    # Check if output is a dict with the expected keys
                    if isinstance(event.output, dict) and 'text_response' in event.output and 'ui_payload' in event.output:
                        text = f"{event.output['text_response']}\n<a2ui-json>\n{json.dumps(event.output['ui_payload'])}\n</a2ui-json>"
                    else:
                        text = str(event.output)
            
            if text:
                last_output = text
                # Send intermediate output
                msg = new_agent_parts_message([Part(root=TextPart(text=text))], task.context_id, task.id)
                await updater.update_status(TaskState.working, msg)

        # Final state
        if last_output:
             await updater.update_status(
                 TaskState.completed,
                 new_agent_parts_message([Part(root=TextPart(text=last_output))], task.context_id, task.id),
                 final=True
             )
        else:
             await updater.update_status(
                 TaskState.completed,
                 new_agent_parts_message([Part(root=TextPart(text="No response from agent"))], task.context_id, task.id),
                 final=True
             )

    async def cancel(self, request: RequestContext, event_queue: EventQueue):
        from a2a.types import UnsupportedOperationError
        from a2a.utils.errors import ServerError
        raise ServerError(error=UnsupportedOperationError())

# Server setup
dummy_card = AgentCard(
    name="a2ui_agent",
    description="A2UI Agent",
    url="http://localhost:8502",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[]
)

app_instance = A2AStarletteApplication(
    agent_card=dummy_card,
    http_handler=DefaultRequestHandler(
        agent_executor=WorkflowAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
)

app = app_instance.build()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8502)
