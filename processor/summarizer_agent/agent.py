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

from processor.schemas import ProcessorResponseModel, SummarizerAIModel, SummarizerResponseModel

import config


class SummarizerAgent:
    def __init__(self):
        self.smith_client = Client()
        self.agent_config = RunnableConfig(
            run_name="assistant_graph",
            tags=["lecture_processor", "DEBUG" if config.debug else "PROD"],
            metadata={
                "agent_version": "v0.0.0",
            },
        )

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

    async def regenerate(
            self,
            extracted_text: str,
            previous_response: str,
            make_test: bool = False,
            custom_instructions: str = "",
            regenerate_tests: bool = True,
            regeneration_instructions: str = "",
            messages_history: list[dict[str, Any]] | None = None,
    ) -> ProcessorResponseModel:

        if messages_history is None:
            messages_history = []

        state = AgentState(
            to_regenerate=True,
            extracted_text=extracted_text,
            previous_response=previous_response,
            regeneration_instructions=regeneration_instructions,
            make_test=make_test,
            custom_instructions=custom_instructions,
            regenerate_tests=regenerate_tests,
            messages_history=messages_history,
        )

        result = await self.graph.ainvoke(state, config=self.agent_config)

        return ProcessorResponseModel(
            summarizer_response=SummarizerResponseModel(
                ai_response=SummarizerAIModel(
                    text=result["ai_response"],
                    title=result["title"],
                ),
                raw_text=extracted_text,
            ),
            test_maker_response=result["generated_tests"],
            total_cost=result["total_cost"],
            messages_history=result["messages_history"],
        )

    async def __call__(
            self,
            extracted_text: str,
            make_test: bool = False,
            custom_instructions: str = "",
    ) -> ProcessorResponseModel:

        state = AgentState(
            extracted_text=extracted_text,
            make_test=make_test,
            custom_instructions=custom_instructions,
        )

        result = await self.graph.ainvoke(state, config=self.agent_config)

        return ProcessorResponseModel(
            summarizer_response=SummarizerResponseModel(
                ai_response=SummarizerAIModel(
                    text=result["ai_response"],
                    title=result["title"],
                ),
                raw_text=extracted_text,
            ),
            test_maker_response=result["generated_tests"],
            total_cost=result["total_cost"],
        )
