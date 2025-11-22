"""Input data models matching UI fields"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SexEnum(str, Enum):
    """Patient sex"""
    male = "male"
    female = "female"
    other = "other"


class LanguageEnum(str, Enum):
    """Supported languages"""
    english = "english"
    hindi = "hindi"
    tamil = "tamil"
    telugu = "telugu"
    bengali = "bengali"


class VitalsInput(BaseModel):
    """Patient vital signs"""
    bp_systolic: Optional[int] = Field(None, ge=60, le=250, description="Systolic blood pressure")
    bp_diastolic: Optional[int] = Field(None, ge=40, le=150, description="Diastolic blood pressure")
    random_glucose: Optional[int] = Field(None, ge=50, le=600, description="Random blood glucose mg/dL")
    temperature_c: Optional[float] = Field(None, ge=35.0, le=42.0, description="Temperature in Celsius")
    heart_rate: Optional[int] = Field(None, ge=40, le=200, description="Heart rate bpm")
    spo2: Optional[int] = Field(None, ge=70, le=100, description="Oxygen saturation %")


class CameraInputs(BaseModel):
    """Camera-captured images (base64 encoded)"""
    conjunctiva_photo: Optional[str] = Field(None, description="Base64 encoded conjunctiva image for anemia")
    swelling_photo: Optional[str] = Field(None, description="Base64 encoded swelling image for maternal risk")
    child_arm_photo: Optional[str] = Field(None, description="Base64 encoded child arm for malnutrition")
    skin_photo: Optional[str] = Field(None, description="Base64 encoded skin for infection/dehydration")
    breathing_video: Optional[str] = Field(None, description="Base64 encoded breathing video (optional)")


class InputPayload(BaseModel):
    """Complete input payload from frontend"""
    
    # Vitals
    vitals: VitalsInput
    
    # Symptoms (list of symptom names)
    symptoms: List[str] = Field(
        default_factory=list,
        description="List of symptoms: fatigue, dizziness, breathlessness, fever, cough, headache, swelling, abdominal_pain, decreased_fetal_movement, etc."
    )
    
    # Camera inputs
    camera_inputs: Optional[CameraInputs] = None
    
    # Patient metadata
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    sex: SexEnum
    pregnant: bool = Field(False, description="Is patient pregnant")
    gestational_weeks: Optional[int] = Field(None, ge=0, le=42, description="Gestational age in weeks")
    
    # Worker and session info
    worker_id: str = Field(..., description="Health worker ID")
    patient_id: str = Field(..., description="Patient ID")
    language: LanguageEnum = Field(LanguageEnum.english, description="Preferred language")
    
    # Offline mode flag
    offline_mode: bool = Field(False, description="Run minimal offline triage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "vitals": {
                    "bp_systolic": 150,
                    "bp_diastolic": 95,
                    "random_glucose": 110,
                    "temperature_c": 37.2,
                    "heart_rate": 88,
                    "spo2": 97
                },
                "symptoms": ["headache", "swelling", "dizziness"],
                "camera_inputs": {
                    "conjunctiva_photo": "base64_encoded_string...",
                    "swelling_photo": "base64_encoded_string..."
                },
                "age": 28,
                "sex": "female",
                "pregnant": True,
                "gestational_weeks": 32,
                "worker_id": "CHW001",
                "patient_id": "PAT12345",
                "language": "hindi",
                "offline_mode": False
            }
        }


class NormalizedContext(BaseModel):
    """Normalized and validated context from Intake Agent"""
    
    # Original payload
    payload: InputPayload
    
    # Validation flags
    is_valid: bool
    validation_errors: List[str] = Field(default_factory=list)
    
    # Computed flags
    has_images: bool
    has_maternal_risk_factors: bool
    has_anemia_symptoms: bool
    requires_urgent_care: bool
    
    # Normalized vitals
    normalized_bp_systolic: Optional[int] = None
    normalized_bp_diastolic: Optional[int] = None
    normalized_glucose: Optional[int] = None
    normalized_heart_rate: Optional[int] = None
    
    # Symptom flags
    symptom_flags: dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "payload": {},
                "is_valid": True,
                "validation_errors": [],
                "has_images": True,
                "has_maternal_risk_factors": True,
                "has_anemia_symptoms": False,
                "requires_urgent_care": False,
                "normalized_bp_systolic": 150,
                "normalized_bp_diastolic": 95,
                "normalized_glucose": 110,
                "normalized_heart_rate": 88,
                "symptom_flags": {
                    "headache": True,
                    "swelling": True,
                    "fatigue": False
                }
            }
        }
