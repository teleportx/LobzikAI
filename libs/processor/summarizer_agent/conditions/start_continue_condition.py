from ...summarizer_agent.state import AgentState


def start_continue_condition(state: AgentState):
    if state.to_regenerate:
        return "regenerate"
    return "summarize"
