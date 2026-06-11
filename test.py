from models.llm import get_llm

llm = get_llm()

response = llm.invoke(
    "What is document comparison?"
)

print(response.content)