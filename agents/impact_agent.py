import json
from langchain_core.prompts import PromptTemplate
from models.llm import get_llm
from prompts.impact_prompt import IMPACT_PROMPT

class ImpactAgent:

    def __init__(self):
        self.llm = get_llm()
        self.prompt = PromptTemplate(
            template=IMPACT_PROMPT,
            input_variables=["change_json"]
        )

    def analyze(self, change_dict):
        chain = self.prompt | self.llm
        response = chain.invoke({
            "change_json": json.dumps(change_dict, indent=2)
        })
        return response.content
