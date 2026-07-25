from langchain_openai import ChatOpenAI

from ...schemas import TestMakerResponseModel
from ...summarizer_agent.state import AgentState
from ...summarizer_agent.utils import count_request_cost


system_prompt = """AI agent wrote some summary (short facts) extracted from some lecture.
You need to complete this generation with generating 10 questions with answers.
Imagine that you are a teacher who makes a test for your students based on the lecture.
Your response is 10 questions with corresponding answers.
"""


def create_generate_tests_node(base_gpt_model: str):
    model = ChatOpenAI(model=base_gpt_model).with_structured_output(
        schema=TestMakerResponseModel,
        include_raw=True,
    )

    async def generate_tests_node(state: AgentState):
        additional = f"""Additional valuable information:
        User wrote a commentary about whole generation (summary + tests). 
        If you know that these instructions can affect test generation, take them into account: 
        {state.regeneration_instructions}""" if state.regeneration_instructions else ""

        messages = [
            {
                "role": "system",
                "content": system_prompt + f"custom user's instructions: {state.custom_instructions}",
            },
            {
                "role": "user",
                "content": state.ai_response + additional,
            },
        ]
        response = await model.ainvoke(messages)

        return {
            "generated_tests": response["parsed"],
            "total_cost": count_request_cost(response["raw"]),
        }

    return generate_tests_node
