from google.genai import types
from google.adk.tools.tool_context import ToolContext

async def record_excuse(excuse: str, tool_context: ToolContext) -> str:
    """
    Records an excuse in the 'Book of Excuses' using ADK Artifacts.
    
    Args:
        excuse (str): The excuse to record.
    """
    filename = "book_of_excuses.md"
    
    # 1. Load existing content if it exists
    existing_content = ""
    try:
        artifact = await tool_context.load_artifact(filename)
        if artifact and artifact.inline_data and artifact.inline_data.data:
             existing_content = artifact.inline_data.data.decode('utf-8')
    except Exception:
        pass

    # If it doesn't exist or is empty, start fresh with a title
    if not existing_content:
        existing_content = "# Book of Excuses\n\n"

    # 2. Append new excuse as a list item
    new_content = existing_content + f"- {excuse}\n"
    
    # 3. Save back
    part = types.Part(inline_data=types.Blob(mime_type="text/plain", data=new_content.encode('utf-8')))
    version = await tool_context.save_artifact(filename, part)
    
    return f"Excuse recorded successfully in '{filename}' (Version {version})."

async def show_excuses(tool_context: ToolContext) -> str:
    """
    Lists all excuses recorded in the 'Book of Excuses'.
    """
    filename = "book_of_excuses.md"
    
    try:
        artifact = await tool_context.load_artifact(filename)
        if artifact and artifact.inline_data and artifact.inline_data.data:
             content = artifact.inline_data.data.decode('utf-8')
             return f"Current Excuses in '{filename}':\n\n{content}"
        else:
             return f"No excuses found in '{filename}' yet."
    except Exception:
         return f"No excuses found in '{filename}' yet."
