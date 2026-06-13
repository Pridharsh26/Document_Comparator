import logging
from typing import Dict

import numpy as np
from models.schemas import DocumentSummary, RuleChange, ChangeType, NumericChange, ComparisonResult
from services.semantic_matcher import SemanticMatcher
from utils.helpers import normalize_text, chunk_list

import re

logger = logging.getLogger(__name__)


def split_into_segments(text: str) -> list:
    text = text.replace("\r\n", "\n")
    raw_blocks = re.split(r"\n{2,}|\r\n{2,}", text)
    segments = [normalize_text(block) for block in raw_blocks if normalize_text(block)]
    return segments


def classify_change(numeric_changes: list, legacy_text: str, modern_text: str) -> str:
    legacy_norm = normalize_text(legacy_text)
    modern_norm = normalize_text(modern_text)
    if legacy_norm == modern_norm:
        return ChangeType.UNCHANGED
    if numeric_changes:
        return ChangeType.MODIFIED
    if legacy_text and modern_text and legacy_norm != modern_norm:
        return ChangeType.MODIFIED
    return ChangeType.UNCHANGED


def detect_changes_for_segments(
    legacy_segments: list,
    modern_segments: list,
    matcher: SemanticMatcher,
    batch_size: int = 64,
) -> list:
    changes: list = []
    num_batches = max(1, (len(legacy_segments) + batch_size - 1) // batch_size)

    for b in range(num_batches):
        start = b * batch_size
        end = min(start + batch_size, len(legacy_segments))
        batch = legacy_segments[start:end]
        if not batch:
            continue
        try:
            sim_matrix = matcher.compute_similarity_matrix(batch, modern_segments)
            for i, legacy_text in enumerate(batch):
                legacy_idx = start + i
                scores = sim_matrix[i]
                best_j = int(np.argmax(scores)) if len(scores) > 0 else -1
                best_score = float(scores[best_j]) if best_j >= 0 else 0.0

                if best_score >= matcher.similarity_threshold:
                    modern_text = modern_segments[best_j]
                    numeric_changes = matcher.detect_numeric_changes(legacy_text, modern_text)
                    change_type = classify_change(numeric_changes, legacy_text, modern_text)
                    changes.append(
                        RuleChange(
                            change_type=change_type,
                            legacy_rule=legacy_text,
                            modernized_rule=modern_text,
                            matched_confidence=best_score,
                            what_changed=numeric_changes,
                        )
                    )
                else:
                    changes.append(
                        RuleChange(
                            change_type=ChangeType.REMOVED,
                            legacy_rule=legacy_text,
                            modernized_rule=None,
                            matched_confidence=best_score,
                        )
                    )
        except Exception as exc:
            logger.error("Batch comparison failed for batch %d: %s", b, exc)
            for legacy_text in batch:
                changes.append(
                    RuleChange(
                        change_type=ChangeType.REMOVED,
                        legacy_rule=legacy_text,
                        modernized_rule=None,
                    )
                )

    return changes


def refine_with_unmatched_modern(changes: list, modern_segments: list, matcher: SemanticMatcher) -> list:
    matched_modern = set()
    for change in changes:
        if change.modernized_rule is not None:
            matched_modern.add(change.modernized_rule)

    for segment in modern_segments:
        if segment not in matched_modern:
            changes.append(
                RuleChange(
                    change_type=ChangeType.ADDED,
                    legacy_rule=None,
                    modernized_rule=segment,
                )
            )
    return changes


def filter_unchanged(changes: list, matcher: SemanticMatcher) -> list:
    filtered = []
    for change in changes:
        if change.change_type == ChangeType.UNCHANGED:
            continue
        filtered.append(change)
    return filtered


def compute_summary(changes: list) -> DocumentSummary:
    added = sum(1 for c in changes if c.change_type == ChangeType.ADDED)
    removed = sum(1 for c in changes if c.change_type == ChangeType.REMOVED)
    modified = sum(1 for c in changes if c.change_type == ChangeType.MODIFIED)
    unchanged = sum(1 for c in changes if c.change_type == ChangeType.UNCHANGED)
    total_legacy = sum(
        1 for c in changes if c.change_type in (ChangeType.MODIFIED, ChangeType.REMOVED, ChangeType.UNCHANGED)
    )
    total_modern = sum(
        1 for c in changes if c.change_type in (ChangeType.MODIFIED, ChangeType.ADDED, ChangeType.UNCHANGED)
    )
    return DocumentSummary(
        total_legacy_rules=total_legacy,
        total_modernized_rules=total_modern,
        added=added,
        removed=removed,
        modified=modified,
        unchanged=unchanged,
    )


def detect_changes(legacy_text: str, modern_text: str, matcher: SemanticMatcher) -> ComparisonResult:
    legacy_segments = split_into_segments(legacy_text)
    modern_segments = split_into_segments(modern_text)

    logger.info("Legacy segments: %d, Modern segments: %d", len(legacy_segments), len(modern_segments))
    changes = detect_changes_for_segments(legacy_segments, modern_segments, matcher)
    changes = refine_with_unmatched_modern(changes, modern_segments, matcher)
    changes = filter_unchanged(changes, matcher)
    summary = compute_summary(changes)
    return ComparisonResult(summary=summary, changes=changes)
