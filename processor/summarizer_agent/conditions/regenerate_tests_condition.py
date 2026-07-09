from langgraph.graph import END

from processor.summarizer_agent.state import AgentState


def regenerate_tests_condition(state: AgentState):
    if state.regenerate_tests and state.make_test:
        return "generate_tests"
    return END
