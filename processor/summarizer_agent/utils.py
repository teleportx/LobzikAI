from langchain_core.messages import AIMessage


def count_request_cost(response: AIMessage) -> int:
    cost = response.response_metadata["token_usage"]["cost"]
    return cost
