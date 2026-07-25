from langgraph.graph import END

from ...summarizer_agent.state import AgentState


def generate_tests_condition(state: AgentState):
    if state.make_test:
        return "generate_tests"
    return END
