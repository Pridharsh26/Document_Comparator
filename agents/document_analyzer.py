import json

from langchain_core.prompts import PromptTemplate

from models.llm import get_llm
from prompts.analyzer_prompt import ANALYZER_PROMPT


class DocumentAnalyzerAgent:

    def __init__(self):

        self.llm = get_llm()

        self.prompt = PromptTemplate(
            template=ANALYZER_PROMPT,
            input_variables=[
                "old_text",
                "new_text"
            ]
        )

    def analyze_change(
        self,
        old_text,
        new_text
    ):

        chain = self.prompt | self.llm

        response = chain.invoke(
            {
                "old_text": old_text,
                "new_text": new_text
            }
        )

        return response.content