from langchain_openai import ChatOpenAI

from processor.summarizer_agent.state import AgentState

import config


def create_regenerate_node():
    model = ChatOpenAI(model=config.AIModels.base_gpt_model)

    async def regenerate_node(state: AgentState):
        prompt = f"Regenerate lecture summary considering following instructions: {state.regeneration_instructions}"
        messages = state.messages_history + [{"role": "user", "content": prompt}]
        response = await model.ainvoke(messages)

        return {
            "ai_response": response.content,
            "messages_history": messages,
        }

    return regenerate_node
