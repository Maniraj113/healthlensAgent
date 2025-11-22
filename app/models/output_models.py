"""Output data models for API responses"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level classification"""
    low = "low"
    moderate = "moderate"
    high = "high"
    urgent = "urgent"


class TriageLevel(str, Enum):
    """Triage priority level"""
    low = "low"
    moderate = "moderate"
    high = "high"
    urgent = "urgent"


class RiskScore(BaseModel):
    """Individual risk score for a domain"""
    score: int = Field(..., ge=0, le=100, description="Risk score 0-100")
    level: RiskLevel = Field(..., description="Risk level classification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "score": 72,
                "level": "high"
            }
        }


class RiskScores(BaseModel):
    """All risk domain scores"""
    anemia: RiskScore
    maternal: RiskScore
    sugar: RiskScore
    infection: Optional[RiskScore] = None
    nutrition: Optional[RiskScore] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "anemia": {"score": 45, "level": "moderate"},
                "maternal": {"score": 88, "level": "high"},
                "sugar": {"score": 20, "level": "low"}
            }
        }


class ReasoningFact(BaseModel):
    """Individual reasoning fact/evidence"""
    fact: str = Field(..., description="The observed fact or evidence")
    weight: int = Field(..., ge=0, le=100, description="Weight/contribution to risk")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this fact")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fact": "BP 150/95",
                "weight": 60,
                "confidence": 0.98
            }
        }


class ImageEvidence(BaseModel):
    """Evidence extracted from images"""
    pallor: bool = Field(False, description="Pallor/anemia detected in conjunctiva")
    pallor_confidence: float = Field(0.0, ge=0.0, le=1.0)
    
    edema_detected: bool = Field(False, description="Edema/swelling detected")
    edema_confidence: float = Field(0.0, ge=0.0, le=1.0)
    
    malnutrition_flag: bool = Field(False, description="Malnutrition indicators detected")
    malnutrition_confidence: float = Field(0.0, ge=0.0, le=1.0)
    
    skin_infection: bool = Field(False, description="Skin infection detected")
    skin_infection_confidence: float = Field(0.0, ge=0.0, le=1.0)
    
    dehydration: bool = Field(False, description="Dehydration signs detected")
    dehydration_confidence: float = Field(0.0, ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "pallor": True,
                "pallor_confidence": 0.82,
                "edema_detected": True,
                "edema_confidence": 0.77,
                "malnutrition_flag": False,
                "malnutrition_confidence": 0.10
            }
        }


class ReasoningResult(BaseModel):
    """Clinical reasoning output"""
    risk_scores: RiskScores
    triage_level: TriageLevel
    reasoning_trace: List[ReasoningFact]
    primary_concern: str = Field(..., description="Primary health concern identified")
    
    class Config:
        json_schema_extra = {
            "example": {
                "risk_scores": {
                    "anemia": {"score": 45, "level": "moderate"},
                    "maternal": {"score": 88, "level": "high"},
                    "sugar": {"score": 20, "level": "low"}
                },
                "triage_level": "high",
                "reasoning_trace": [
                    {"fact": "BP 150/95", "weight": 60, "confidence": 0.98},
                    {"fact": "Edema detected", "weight": 20, "confidence": 0.82}
                ],
                "primary_concern": "maternal_hypertension"
            }
        }


class ActionPlan(BaseModel):
    """Action plan and communication output"""
    summary_text: str = Field(..., description="Plain language summary")
    action_checklist: List[str] = Field(..., description="Actionable steps for worker")
    emergency_signs: List[str] = Field(default_factory=list, description="Warning signs to watch for")
    voice_text: str = Field(..., description="Text for TTS output")
    language: str = Field(..., description="Language of the output")
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary_text": "High maternal risk due to elevated BP and swelling. Refer to PHC immediately.",
                "action_checklist": [
                    "Arrange transport to PHC",
                    "Avoid physical exertion",
                    "Visit PHC urgently within 2 hours"
                ],
                "emergency_signs": [
                    "Severe headache",
                    "Vision changes",
                    "Seizures"
                ],
                "voice_text": "High maternal risk. Please visit the primary health center immediately.",
                "language": "hindi"
            }
        }


class FinalResult(BaseModel):
    """Final API response to frontend"""
    visit_id: str = Field(..., description="Unique visit identifier")
    risk_scores: RiskScores
    triage_level: TriageLevel
    summary_text: str
    action_checklist: List[str]
    emergency_signs: List[str] = Field(default_factory=list)
    voice_text: str
    reasons: List[ReasoningFact]
    image_evidence: Optional[ImageEvidence] = None
    timestamp: str = Field(..., description="ISO timestamp of analysis")
    offline_processed: bool = Field(False, description="Was this processed in offline mode")
    
    class Config:
        json_schema_extra = {
            "example": {
                "visit_id": "v123",
                "risk_scores": {
                    "anemia": {"score": 72, "level": "high"},
                    "maternal": {"score": 88, "level": "high"},
                    "sugar": {"score": 20, "level": "low"}
                },
                "triage_level": "high",
                "summary_text": "High maternal risk due to elevated BP and swelling. Refer to PHC immediately.",
                "action_checklist": [
                    "Arrange transport",
                    "Avoid physical exertion",
                    "Visit PHC urgently"
                ],
                "emergency_signs": [
                    "Severe headache",
                    "Vision changes"
                ],
                "voice_text": "High maternal risk. Please visit the primary health center immediately.",
                "reasons": [
                    {"fact": "BP 150/95", "weight": 60, "confidence": 0.98},
                    {"fact": "Edema detected", "weight": 20, "confidence": 0.82}
                ],
                "image_evidence": {
                    "pallor": False,
                    "pallor_confidence": 0.10,
                    "edema_detected": True,
                    "edema_confidence": 0.82
                },
                "timestamp": "2024-01-15T10:30:00Z",
                "offline_processed": False
            }
        }
