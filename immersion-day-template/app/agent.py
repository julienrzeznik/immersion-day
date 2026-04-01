import os
from dotenv import load_dotenv
from google.adk.apps import App
from .versions import get_agent

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

root_agent = get_agent()

app = App(
    root_agent=root_agent,
    name="app",
)
