"""Intake Agent - Validates and normalizes input data"""

from google.adk.agents import LlmAgent
from typing import Dict, Any
import uuid
from datetime import datetime
import logging

from ..models.input_models import InputPayload, NormalizedContext
from ..tools.validation_tools import (
    validate_vitals,
    normalize_symptoms,
    check_mandatory_fields,
    compute_derived_flags,
)


logger = logging.getLogger(__name__)


def validate_and_normalize_input(payload_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Validate and normalize the input payload.
    
    This tool validates vitals, normalizes symptoms, checks mandatory fields,
    and computes derived flags.
    
    Args:
        payload_dict: Raw input payload as dictionary
    
    Returns:
        Normalized context dictionary
    """
    # Validate vitals
    vitals = payload_dict.get("vitals", {})
    vitals_valid, vitals_errors = validate_vitals(vitals)
    
    # Check mandatory fields
    fields_complete, missing_fields = check_mandatory_fields(payload_dict)
    
    # Normalize symptoms
    symptoms = payload_dict.get("symptoms", [])
    symptom_flags = normalize_symptoms(symptoms)
    
    # Compute derived flags
    derived_flags = compute_derived_flags(payload_dict, symptom_flags)
    
    # Combine validation results
    all_errors = []
    if not vitals_valid:
        all_errors.extend(vitals_errors)
    if not fields_complete:
        all_errors.extend([f"Missing field: {f}" for f in missing_fields])
    
    is_valid = len(all_errors) == 0
    
    # Create normalized context
    normalized_context = {
        "payload": payload_dict,
        "is_valid": is_valid,
        "validation_errors": all_errors,
        "has_images": derived_flags.get("has_images", False),
        "has_maternal_risk_factors": derived_flags.get("has_maternal_risk_factors", False),
        "has_anemia_symptoms": derived_flags.get("has_anemia_symptoms", False),
        "requires_urgent_care": derived_flags.get("requires_urgent_care", False),
        "normalized_bp_systolic": vitals.get("bp_systolic"),
        "normalized_bp_diastolic": vitals.get("bp_diastolic"),
        "normalized_glucose": vitals.get("random_glucose"),
        "normalized_heart_rate": vitals.get("heart_rate"),
        "symptom_flags": symptom_flags,
    }
    
    return normalized_context


def run_offline_triage(payload_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Run minimal offline rule-based triage.
    
    When network is unavailable, this provides basic risk assessment
    using simple rules without AI models.
    
    Args:
        payload_dict: Input payload dictionary
    
    Returns:
        Basic triage result
    """
    vitals = payload_dict.get("vitals", {})
    symptoms = payload_dict.get("symptoms", [])
    pregnant = payload_dict.get("pregnant", False)
    
    # Simple rule-based triage
    risk_level = "low"
    summary = "Basic health check completed."
    actions = ["Continue routine monitoring"]
    
    # Check for urgent maternal risk
    bp_sys = vitals.get("bp_systolic")
    bp_dia = vitals.get("bp_diastolic")
    
    if pregnant and bp_sys is not None and bp_sys >= 140:
        risk_level = "urgent"
        summary = "High blood pressure detected in pregnant patient. Seek immediate medical care."
        actions = ["Go to health center immediately", "Do not delay"]
    
    # Check for high glucose
    glucose = vitals.get("random_glucose")
    if glucose is not None and glucose >= 200:
        risk_level = "high"
        summary = "High blood sugar detected. Medical consultation needed."
        actions = ["Visit health center within 24 hours", "Follow dietary advice"]
    
    # Check for fever
    elif "fever" in [s.lower() for s in symptoms]:
        risk_level = "moderate"
        summary = "Fever detected. Monitor and seek care if worsens."
        actions = ["Rest and hydrate", "Monitor temperature", "Visit health center if fever persists"]
    
    return {
        "visit_id": f"offline_{uuid.uuid4().hex[:8]}",
        "risk_scores": {
            "anemia": {"score": 0, "level": "low"},
            "maternal": {"score": 0, "level": "low"},
            "sugar": {"score": 0, "level": "low"}
        },
        "triage_level": risk_level,
        "summary_text": summary,
        "action_checklist": actions,
        "emergency_signs": [],
        "voice_text": summary,
        "reasons": [
            {"fact": "Basic rule-based triage performed", "weight": 50, "confidence": 0.8}
        ],
        "image_evidence": None,
        "timestamp": datetime.utcnow().isoformat(),
        "offline_processed": True,
    }


def create_intake_agent() -> LlmAgent:
    """
    Create the Intake Agent.
    
    Purpose:
    - Validate and normalize raw vitals and symptoms
    - Check mandatory fields
    - Decide which downstream agents to trigger
    - Build normalized_context JSON
    - Store initial record in DB
    - Run offline triage if requested
    
    Returns:
        Configured LlmAgent for intake processing
    """
    agent = LlmAgent(
        model="gemini-2.0-flash-exp",
        name="intake_agent",
        instruction="""You are the Intake Agent for a health triage system.

Your responsibilities:
1. Validate the input payload using the validate_and_normalize_input tool
2. Check if all required fields are present and vitals are in valid ranges
3. Normalize symptoms into standardized flags
4. Compute derived flags (has_images, has_maternal_risk_factors, etc.)
5. If offline_mode is True in the payload, use run_offline_triage tool instead
6. Return the normalized_context as your final output

Always use the tools provided. Do not make up data.
If validation fails, include all error messages in the output.
""",
        description="Validates and normalizes patient input data, performs initial triage",
        tools=[validate_and_normalize_input, run_offline_triage],
    )
    
    return agent
