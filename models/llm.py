from langchain_openai import ChatOpenAI


def get_llm():

    llm = ChatOpenAI(
        model="deepseek-7b",
        api_key="abc-123",
        base_url="http://localhost:8000/v1",
        temperature=0
    )

    return llm