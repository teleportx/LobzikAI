from langchain_openai import ChatOpenAI

from processor.summarizer_agent.state import AgentState

import config


system_prompt = """You are an assistant who makes titles.
You are provided summarized version of some lecture. Your task - give a short title.
Title must be shorter than 5 words, but represent main reason of lecture."""


def create_title_node():
    model = ChatOpenAI(
        model=config.AIModels.base_gpt_model,
        max_completion_tokens=32,
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

        return {"title": response.content}

    return title_node
