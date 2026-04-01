import os

from google.genai import types
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools.bash_tool import ExecuteBashTool, BashToolPolicy
import pathlib
from google.adk.skills import load_skill_from_gcs_dir, load_skill_from_dir, list_skills_in_gcs_dir, list_skills_in_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.code_executors.unsafe_local_code_executor import UnsafeLocalCodeExecutor

from app.config import SKILLS_URI

skills_uri = SKILLS_URI

# 1. Load the skills either from GCS or locally
skills = []
if skills_uri.startswith("gs://"):
    bucket_name = skills_uri.replace("gs://", "").split("/")[0]
    # Optionally parse path if available, but for now we assume root of bucket
    available = list_skills_in_gcs_dir(bucket_name=bucket_name)
    for skill_id in available.keys():
        skills.append(
            load_skill_from_gcs_dir(
                bucket_name=bucket_name,
                skill_id=skill_id
            )
        )
else:
    skill_path_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), skills_uri)
    available = list_skills_in_dir(skill_path_base)
    for skill_id in available.keys():
        skills.append(
            load_skill_from_dir(os.path.join(skill_path_base, skill_id))
        )

# 2. Add it to a SkillToolset
skill_toolset = SkillToolset(
    skills=skills,
    code_executor=UnsafeLocalCodeExecutor()
)

# 3. Create the agent with the toolset
root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    You are an intelligent assistant with access to ADK Skills.
    Always prioritize using your tools to read available skills and follow their instructions carefully.
    """,
    tools=[
        skill_toolset,
        ExecuteBashTool(
            workspace=pathlib.Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            policy=BashToolPolicy(allowed_command_prefixes=("echo", "ls", "cat", "python"))
        )
    ],
)
