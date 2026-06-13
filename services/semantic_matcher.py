import logging
from typing import List, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

from models.schemas import ChangeType, NumericChange
from utils.helpers import normalize_text, extract_numeric_values

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.85


class SemanticMatcher:
    def __init__(self, similarity_threshold: float = SIMILARITY_THRESHOLD):
        self.similarity_threshold = similarity_threshold
        self.model: Optional[SentenceTransformer] = None

    def _load_model(self) -> SentenceTransformer:
        if self.model is None:
            logger.info("Loading embedding model: %s", MODEL_NAME)
            self.model = SentenceTransformer(MODEL_NAME)
        return self.model

    def _encode_batch(self, texts: List[str]) -> np.ndarray:
        model = self._load_model()
        embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings

    def compute_similarity_matrix(self, legacy_texts: List[str], modern_texts: List[str]) -> np.ndarray:
        logger.info("Computing embeddings for %d legacy and %d modern segments", len(legacy_texts), len(modern_texts))
        all_texts = legacy_texts + modern_texts
        embeddings = self._encode_batch(all_texts)
        legacy_emb = embeddings[: len(legacy_texts)]
        modern_emb = embeddings[len(legacy_texts) :]
        norm_legacy = legacy_emb / (np.linalg.norm(legacy_emb, axis=1, keepdims=True) + 1e-9)
        norm_modern = modern_emb / (np.linalg.norm(modern_emb, axis=1, keepdims=True) + 1e-9)
        similarity_matrix = np.dot(norm_legacy, norm_modern.T)
        return similarity_matrix

    def match_segments(
        self, legacy_segments: List[str], modern_segments: List[str]
    ) -> Tuple[List[int], List[int], List[Tuple[int, int, float]]]:
        similarity_matrix = self.compute_similarity_matrix(legacy_segments, modern_segments)
        matches: List[Tuple[int, int, float]] = []
        matched_modern = set()
        matched_legacy = set()

        rows, cols = similarity_matrix.shape
        flat_pairs = []
        for i in range(rows):
            for j in range(cols):
                flat_pairs.append((similarity_matrix[i, j], i, j))
        flat_pairs.sort(key=lambda x: x[0], reverse=True)

        for score, i, j in flat_pairs:
            if score < self.similarity_threshold:
                break
            if i in matched_legacy or j in matched_modern:
                continue
            matched_legacy.add(i)
            matched_modern.add(j)
            matches.append((i, j, float(score)))

        return matched_legacy, matched_modern, matches

    @staticmethod
    def detect_numeric_changes(legacy_text: str, modern_text: str) -> List[NumericChange]:
        changes = []
        legacy_nums = extract_numeric_values(legacy_text)
        modern_nums = extract_numeric_values(modern_text)

        max_len = max(len(legacy_nums), len(modern_nums))
        for idx in range(max_len):
            old_val = legacy_nums[idx] if idx < len(legacy_nums) else None
            new_val = modern_nums[idx] if idx < len(modern_nums) else None
            if old_val is not None and new_val is not None and old_val != new_val:
                changes.append(
                    NumericChange(
                        field="numeric_value",
                        old_value=old_val,
                        new_value=new_val,
                    )
                )
        return changes

    @staticmethod
    def is_semantically_same(legacy_text: str, modern_text: str, threshold: float = 0.85) -> bool:
        matcher = SemanticMatcher(similarity_threshold=threshold)
        similarity_matrix = matcher.compute_similarity_matrix([legacy_text], [modern_text])
        return bool(similarity_matrix[0, 0] >= threshold)
