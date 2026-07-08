from processor.summarizer_agent.state import AgentState


def start_continue_condition(state: AgentState):
    if state.messages_history:
        return "regenerate"
    return "summarize"
