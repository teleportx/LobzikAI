import warnings

warnings.filterwarnings(
    "ignore",
    message=r".*PydanticSerializationUnexpectedValue.*",
)

from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langsmith import Client

from .state import AgentState
from .nodes import (
    create_generate_tests_node,
    create_regenerate_node,
    create_summarize_node,
    create_title_node,
)

from .conditions import (
    generate_tests_condition,
    regenerate_tests_condition,
    start_continue_condition,
)

from processor.schemas import ProcessorResponseModel, SummarizerResponseModel, SummarizerAIModel

import config


class SummarizerAgent:
    def __init__(self):
        self.smith_client = Client()

        graph = StateGraph(AgentState)

        graph.add_node("generate_tests", create_generate_tests_node())
        graph.add_node("regenerate", create_regenerate_node())
        graph.add_node("summarize", create_summarize_node())
        graph.add_node("title_maker", create_title_node())

        graph.add_conditional_edges(START, start_continue_condition)
        graph.add_edge("summarize", "title_maker")
        graph.add_conditional_edges("summarize", generate_tests_condition)
        graph.add_conditional_edges("regenerate", regenerate_tests_condition)
        graph.add_edge("title_maker", END)
        graph.add_edge("generate_tests", END)

        self.graph = graph.compile()

    async def __call__(
            self,
            extracted_text: str,
            make_test: bool = False,
            messages_history: list[dict[str, Any]] | None = None,
            regenerate_tests: bool = True,
            custom_instructions: str = "",
            regeneration_instructions: str = "",
    ) -> ProcessorResponseModel:

        if messages_history is None:
            messages_history = []

        state = AgentState(
            extracted_text=extracted_text,
            make_test=make_test,
            messages_history=messages_history,
            regenerate_tests=regenerate_tests,
            custom_instructions=custom_instructions,
            regeneration_instructions=regeneration_instructions,
        )
        agent_config = RunnableConfig(
            run_name="assistant_graph",
            tags=["lecture_processor", "DEBUG" if config.debug else "PROD"],
            metadata={
                "agent_version": "v0.0.0",
            },
        )

        result = await self.graph.ainvoke(state, config=agent_config)

        return ProcessorResponseModel(
            summarizer_response=SummarizerResponseModel(
                ai_response=SummarizerAIModel(
                    text=result["ai_response"],
                    title=result["title"],
                ),
                raw_text=extracted_text,
            ),
            test_maker_response=result["generated_tests"],
            messages_history=result["messages_history"],
            total_cost=result["total_cost"],
        )
