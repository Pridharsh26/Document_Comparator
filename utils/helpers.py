import hashlib
import logging
import re
from typing import Any, Dict
import functools
import pandas as pd

logger = logging.getLogger(__name__)


def compute_file_hash(file_path: str) -> str:
    try:
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as exc:
        logger.warning("Failed to hash file %s: %s", file_path, exc)
        return ""


def extract_numeric_values(text: str) -> list:
    pattern = re.compile(r"\b\d+(?:[.,]\d+)?\b")
    return pattern.findall(text)


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = text.lower()
    return text


def safe_json(obj: Any) -> Dict:
    try:
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        return dict(obj) if isinstance(obj, dict) else {"data": str(obj)}
    except Exception as exc:
        logger.error("Failed to serialize object to JSON: %s", exc)
        return {"error": str(exc)}


def chunk_list(lst: list, chunk_size: int) -> list:
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def timed_cache(seconds: int = 300):
    def decorator(func):
        cache: Dict[str, Any] = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            if key in cache:
                result, timestamp = cache[key]
                import time

                if time.time() - timestamp < seconds:
                    return result
            result = func(*args, **kwargs)
            import time

            cache[key] = (result, time.time())
            return result

        return wrapper

    return decorator


def to_dataframe(changes: list) -> pd.DataFrame:
    rows = []
    for change in changes:
        rows.append(
            {
                "Change Type": change.change_type,
                "Legacy Rule": change.legacy_rule,
                "Modernized Rule": change.modernized_rule,
                "Confidence": change.matched_confidence,
                "Impact Level": change.impact_level,
                "Risk Level": change.risk_level,
                "Priority Level": change.priority_level,
                "Summary": change.business_explanation,
            }
        )
    return pd.DataFrame(rows)
