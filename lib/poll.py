agent_action: bool = False

def toggle():
    global agent_action
    agent_action = not agent_action

def get():
    return agent_action
