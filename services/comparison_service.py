import json

from tools.chunking import create_chunks
from tools.semantic_search import SemanticComparator

from agents.document_analyzer import (
    DocumentAnalyzerAgent
)


class ComparisonService:

    def __init__(self):

        self.comparator = SemanticComparator()

        self.agent = DocumentAnalyzerAgent()

    def compare_documents(
        self,
        old_text,
        new_text
    ):

        old_chunks = create_chunks(old_text)

        new_chunks = create_chunks(new_text)

        matched_chunks = self.comparator.compare(
            old_chunks,
            new_chunks
        )

        final_output = []

        for item in matched_chunks:

            result = self.agent.analyze_change(
                item["old_chunk"],
                item["new_chunk"]
            )

            try:

                final_output.append(
                    json.loads(result)
                )

            except:

                pass

        return {
            "changes": final_output
        }