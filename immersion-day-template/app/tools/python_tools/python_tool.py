from google.adk.tools.tool_context import ToolContext

def generate_excuse(thing: str, context: ToolContext) -> str:
    """
    Generates a completely absurd excuse for not doing something
    
    Args:
        thing (str): The name of the thing the user is looking an excuse for
    """
    
    # A list of classic, absurd technical excuses
    excuses = [
        "My cat is asleep on my keyboard and it's strictly against the law to move her.",
        "My dog ate my VPN token.",
        "I'm currently engaged in a high-stakes staring contest with my rubber duck.",
        "My Wi-Fi router is experiencing a severe existential crisis.",
        "I accidentally compiled my brain into an infinite loop and need a hard reboot.",
        "I'm waiting for my smart coffee mug to finish updating its firmware.",
        "The code works perfectly on my machine, so I am taking the day off to celebrate.",
        "I forgot my password and I'm too embarrassed to ask IT to reset it for the third time this week.",
        "The model I was training decided to take a personal day, so I have to stay home and provide emotional support."
    ]
    
    # Deterministic selection logic: sum the ASCII values of the input string
    ascii_sum = sum(ord(char) for char in thing)
    
    # Use modulo to pick an index that is always within the bounds of the list
    excuse_index = ascii_sum % len(excuses)
    selected_excuse = excuses[excuse_index]

    # Update existing state (specific to the session)
    count = context.state.get("user_excuses_count", 0)
    context.state["user_excuses_count"] = count + 1

    # Add new state (temporary, only for the current invocation)
    context.state["temp:last_operation_status"] = "success"

    return f"Regarding '{thing}': {selected_excuse}"
