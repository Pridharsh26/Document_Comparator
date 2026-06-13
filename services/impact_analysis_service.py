import json
from agents.impact_agent import ImpactAgent

class ImpactAnalysisService:

    def __init__(self):
        self.agent = ImpactAgent()

    def analyze(self, comparison_result):
        changes = comparison_result.get("changes", [])
        impact_results = []

        for change in changes:
            try:
                result = self.agent.analyze(change)
                impact_results.append(json.loads(result))
            except:
                pass

        return {
            "impact_analysis": impact_results
        }

    # ⭐ ADD THIS METHOD
    def to_vector_texts(self, impact_result):
        texts = []
        for item in impact_result["impact_analysis"]:
            text = (
                f"Change Summary: {item.get('change_summary', '')}\n"
                f"Risk Level: {item.get('risk_level', '')}\n"
                f"Business Impact: {item.get('business_impact', '')}\n"
                f"Compliance Impact: {item.get('compliance_impact', '')}\n"
                f"Recommended Action: {item.get('recommended_action', '')}"
            )
            texts.append(text)
        return texts
