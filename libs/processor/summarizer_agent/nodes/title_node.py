from langchain_openai import ChatOpenAI

from ...summarizer_agent.state import AgentState
from ...summarizer_agent.utils import count_request_cost


system_prompt = """You are an assistant who makes titles.
You are provided summarized version of some lecture. Your task - give a short title.
Title must be shorter than 5 words, but represent main reason of lecture."""


def create_title_node(base_gpt_model: str):
    model = ChatOpenAI(
        model=base_gpt_model,
        max_completion_tokens=32,
        reasoning_effort="low",
    )

    async def title_node(state: AgentState):
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": state.ai_response,
            },
        ]
        response = await model.ainvoke(messages)

        return {
            "title": response.content,
            "total_cost": count_request_cost(response),
        }

    return title_node
