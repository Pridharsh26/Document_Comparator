import logging
from typing import List, Optional, Dict, Any

from models.schemas import ComparisonResult, RuleChange, ChangeType, NumericChange
from services.rag_service import RagService
from services.ollama_service import ChatOllamaService

logger = logging.getLogger(__name__)


class LlmDocumentAnalyzer:
    def __init__(self, rag_service: RagService, ollama: ChatOllamaService, similarity_threshold: float = 0.85):
        self.rag_service = rag_service
        self.ollama = ollama
        self.similarity_threshold = similarity_threshold

    def analyze(self, legacy_text: str, modern_text: str, file_info: Optional[dict] = None) -> dict:
        query = " ".join([legacy_text[:600], modern_text[:600]])
        context = self.rag_service.retrieve(query)

        prompt = (
            "You are an expert document comparison engine.\n"
            "Use the provided HR policy context as external knowledge.\n\n"
            f"Context:\n{context}\n\n"
            "Compare:\n"
            f"Legacy:\n{legacy_text}\n\n"
            f"Modernized:\n{modern_text}\n\n"
            "Ignore numbering or position. Focus on semantic meaning. Treat wording-only changes as unchanged when meaning is identical.\n\n"
            "Return JSON ONLY with this schema:\n"
            '{"summary": {"total_legacy_rules": 0, "total_modernized_rules": 0, "added": 0, "removed": 0, "modified": 0, "unchanged": 0}, '
            '"changes": [{"change_type": "ADDED|REMOVED|MODIFIED|UNCHANGED", "legacy_rule": "", "modernized_rule": "", "matched_confidence": 0.0, "what_changed": []}]}'
        )
        schema = (
            "JSON with summary and changes. change_type must be one of ADDED/REMOVED/MODIFIED/UNCHANGED. "
            "numeric changes in what_changed as list of {field, old_value, new_value}."
        )
        raw = self.ollama.invoke(f"{prompt}\nOutput contract:\n{schema}")
        return self._parse_result(raw)

    def _parse_result(self, raw: str) -> dict:
        import json

        try:
            data = json.loads(raw)
            data.setdefault("summary", {})
            data.setdefault("changes", [])
            if "business_recommendations" not in data:
                data["business_recommendations"] = []
            if "risk_assessment" not in data:
                data["risk_assessment"] = ""
            return ComparisonResult(**data)
        except Exception as exc:
            logger.error("Failed to parse LLM analysis output: %s", exc)
            return self._fallback_result(raw)

    def _fallback_result(self, raw: str) -> dict:
        return ComparisonResult(
            summary=ComparisonResult(
                summary={
                    "total_legacy_rules": 0,
                    "total_modernized_rules": 0,
                    "added": 0,
                    "removed": 0,
                    "modified": 0,
                    "unchanged": 0,
                }
            ),
            changes=[
                RuleChange(
                    change_type=ChangeType.UNCHANGED,
                    legacy_rule=raw,
                    modernized_rule=raw,
                )
            ],
            business_recommendations=["Review LLM output format."],
            risk_assessment="Unable to parse automated output; manual review required.",
        )
