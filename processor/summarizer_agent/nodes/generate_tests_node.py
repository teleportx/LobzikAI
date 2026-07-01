from langchain_openai import ChatOpenAI

from processor.summarizer_agent.state import AgentState
from processor.schemas import TestMakerResponseModel

import config


system_prompt = """AI agent wrote some summary (short facts) extracted from some lecture.
You need to complete this generation with generating 10 questions with answers.
Imagine that you are a teacher who makes a test for your students based on the lecture.
Your response is 10 questions with corresponding answers.
"""


def create_generate_tests_node():
    model = ChatOpenAI(model=config.AIModels.base_gpt_model).with_structured_output(
        schema=TestMakerResponseModel,
    )
    async def generate_tests_node(state: AgentState):
        additional = f"""Additional valuable information:
        User wrote a commentary about whole generation (summary + tests). 
        If you know that these instructions can affect test generation, 
        take them into account: {state.custom_instructions}""" if state.custom_instructions else ""

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": state.ai_response + additional,
            },
        ]
        response: TestMakerResponseModel = await model.ainvoke(messages)

        return {"generated_tests": response}

    return generate_tests_node
