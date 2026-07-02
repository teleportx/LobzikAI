from langchain_openai import ChatOpenAI

from processor.summarizer_agent.state import AgentState

import config


system_prompt = """You are an assistant who makes a brief of some lecture.
You need to extract all facts from lecture. Your result - a list of facts.
Input data is noisy, so pay attention only at facts, but save a whole sense of lecture.
Don't lose any details about facts.
(not dialogues, appeals or some phrases not related to lecture)
All output data must be in markdown format. Sort all facts by their topic. 
Before every group of facts with the same topic, put jews a header.
"""


def create_summarize_node():
    model = ChatOpenAI(model=config.AIModels.sum_model)

    async def summarizer_node(state: AgentState):
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": state.extracted_text + f"Take into account user's instructions: {system_prompt}",
            },
        ]
        response = await model.ainvoke(messages)
        ai_message = {
            "role": "assistant",
            "content": response.content,
        }

        return {
            "ai_response": response.content,
            "messages_history": messages + [ai_message],
        }

    return summarizer_node
