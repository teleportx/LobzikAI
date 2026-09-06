from langgraph.graph import END

from ...summarizer_agent.state import AgentState


def regenerate_tests_condition(state: AgentState):
    if state.regenerate_tests and state.make_test:
        return "generate_tests"
    return END
