from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ChangeType(str, Enum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"
    UNCHANGED = "UNCHANGED"


class NumericChange(BaseModel):
    field: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class RuleChange(BaseModel):
    change_type: ChangeType
    legacy_rule: Optional[str] = None
    modernized_rule: Optional[str] = None
    matched_confidence: Optional[float] = None
    what_changed: List[NumericChange] = Field(default_factory=list)
    impact_categories: List[str] = Field(default_factory=list)
    impact_level: str = "Medium"
    risk_level: str = "Medium"
    priority_level: str = "Medium"
    business_explanation: Optional[str] = None
    affected_parties: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    drawbacks: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class DocumentSummary(BaseModel):
    total_legacy_rules: int
    total_modernized_rules: int
    added: int
    removed: int
    modified: int
    unchanged: int


class ComparisonResult(BaseModel):
    summary: DocumentSummary
    changes: List[RuleChange]
    business_recommendations: List[str] = Field(default_factory=list)
    risk_assessment: str = ""


class AgentStatus(BaseModel):
    agent_name: str
    status: str
    message: str


class AnalysisResponse(BaseModel):
    success: bool
    comparison: Optional[ComparisonResult] = None
    status_log: List[AgentStatus] = Field(default_factory=list)
    error: Optional[str] = None


class ExportFormat(str, Enum):
    JSON = "json"
    PDF = "pdf"
    EXCEL = "excel"
