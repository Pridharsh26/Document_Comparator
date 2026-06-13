import logging
from typing import Optional

from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel

logger =logging.getLogger(__name__)


class ChatOllamaService:
    def __init__(self, model_name: str = "llama3:8b-instruct"):
        self.model_name = model_name
        self._llm: Optional[ChatOllama] = None

    @property
    def llm(self) -> ChatOllama:
        if self._llm is None:
            self._llm = ChatOllama(model=self.model_name, temperature=0.1)
        return self._llm

    def invoke(self, prompt: str) -> str:
        message = ChatPromptTemplate.from_template("{prompt}").format_messages(prompt=prompt)
        response = self.llm.invoke(message)
        content = response.content if hasattr(response, "content") else str(response)
        return content.content if hasattr(content, "content") else str(content)
