from langchain_openai import ChatOpenAI

from ...summarizer_agent.state import AgentState
from ...summarizer_agent.utils import count_request_cost


system_prompt = """You are an assistant who makes a brief of some lecture.
You need to extract all facts from lecture. Your result - a list of facts.
Input data is noisy, so pay attention only at facts, but save a whole sense of lecture.
Don't lose any details about facts.
(not dialogues, appeals or some phrases not related to lecture)
All output data must be in markdown format. Sort all facts by their topic. 
Before every group of facts with the same topic, put a header.
"""


def create_summarize_node(sum_model: str):
    model = ChatOpenAI(model=sum_model)

    async def summarizer_node(state: AgentState):
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": state.extracted_text + f"Take into account user's instructions: {state.custom_instructions}",
            },
        ]
        response = await model.ainvoke(messages)

        return {
            "ai_response": response.content,
            "total_cost": count_request_cost(response),
        }

    return summarizer_node
