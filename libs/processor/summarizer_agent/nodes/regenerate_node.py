from langchain_openai import ChatOpenAI

from ...summarizer_agent.state import AgentState
from ...summarizer_agent.utils import count_request_cost


system_prompt = """Assistant generated a brief of lecture containing much noise and
other information not related to the lecture due to OCR defects. 
Your task is to fix the brief considering all instructions you will be given."""


def create_regenerate_node(base_gpt_model: str):
    model = ChatOpenAI(model=base_gpt_model)

    async def regenerate_node(state: AgentState):
        messages = state.messages_history.copy()
        if not messages:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": f"""Extracted lecture text: {state.extracted_text}
                    Custom user's instructions: {state.custom_instructions}""",
                },
            ]

        new_messages = [
            {
                "role": "assistant",
                "content": state.previous_response,
            },
            {
                "role": "user",
                "content": f"User's commentaries about last generation: {state.regeneration_instructions}"
            },
        ]
        messages.extend(new_messages)

        response = await model.ainvoke(messages)

        return {
            "ai_response": response.content,
            "messages_history": messages,
            "total_cost": count_request_cost(response),
        }

    return regenerate_node
