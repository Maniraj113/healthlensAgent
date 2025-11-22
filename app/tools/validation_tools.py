"""Validation and normalization tools for Intake Agent"""

from typing import Dict, List, Tuple, Any
from ..models.input_models import InputPayload, VitalsInput


def validate_vitals(vitals: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate vital signs are within acceptable ranges.
    
    Args:
        vitals: Dictionary of vital sign values
    
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    # Blood pressure validation
    bp_sys = vitals.get("bp_systolic")
    bp_dia = vitals.get("bp_diastolic")
    
    if bp_sys is not None:
        if bp_sys < 60 or bp_sys > 250:
            errors.append(f"Systolic BP {bp_sys} out of range (60-250)")
        if bp_dia is not None and bp_sys <= bp_dia:
            errors.append(f"Systolic BP must be greater than diastolic BP")
    
    if bp_dia is not None:
        if bp_dia < 40 or bp_dia > 150:
            errors.append(f"Diastolic BP {bp_dia} out of range (40-150)")
    
    # Glucose validation
    glucose = vitals.get("random_glucose")
    if glucose is not None:
        if glucose < 50 or glucose > 600:
            errors.append(f"Glucose {glucose} out of range (50-600 mg/dL)")
    
    # Temperature validation
    temp = vitals.get("temperature_c")
    if temp is not None:
        if temp < 35.0 or temp > 42.0:
            errors.append(f"Temperature {temp}°C out of range (35-42°C)")
    
    # Heart rate validation
    hr = vitals.get("heart_rate")
    if hr is not None:
        if hr < 40 or hr > 200:
            errors.append(f"Heart rate {hr} out of range (40-200 bpm)")
    
    # SpO2 validation
    spo2 = vitals.get("spo2")
    if spo2 is not None:
        if spo2 < 70 or spo2 > 100:
            errors.append(f"SpO2 {spo2}% out of range (70-100%)")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def normalize_symptoms(symptoms: List[str]) -> Dict[str, bool]:
    """
    Normalize symptom list into a dictionary of flags.
    
    Args:
        symptoms: List of symptom strings
    
    Returns:
        Dictionary mapping symptom names to boolean flags
    """
    # Known symptoms
    known_symptoms = [
        "fatigue",
        "dizziness",
        "breathlessness",
        "fever",
        "cough",
        "headache",
        "swelling",
        "abdominal_pain",
        "decreased_fetal_movement",
        "nausea",
        "vomiting",
        "chest_pain",
        "palpitations",
        "blurred_vision",
    ]
    
    # Normalize to lowercase and create flags
    symptom_flags = {}
    normalized_symptoms = [s.lower().strip().replace(" ", "_") for s in symptoms]
    
    for symptom in known_symptoms:
        symptom_flags[symptom] = symptom in normalized_symptoms
    
    return symptom_flags


def check_mandatory_fields(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Check that all mandatory fields are present.
    
    Args:
        payload: Input payload dictionary
    
    Returns:
        Tuple of (is_complete, list of missing fields)
    """
    missing = []
    
    # Mandatory fields
    required_fields = [
        "age",
        "sex",
        "worker_id",
        "patient_id",
    ]
    
    for field in required_fields:
        if field not in payload or payload[field] is None:
            missing.append(field)
    
    # If pregnant, gestational_weeks should be present
    if payload.get("pregnant", False):
        if "gestational_weeks" not in payload or payload["gestational_weeks"] is None:
            missing.append("gestational_weeks (required for pregnant patients)")
    
    is_complete = len(missing) == 0
    return is_complete, missing


def compute_derived_flags(payload: Dict[str, Any], symptom_flags: Dict[str, bool]) -> Dict[str, bool]:
    """
    Compute derived boolean flags from payload.
    
    Args:
        payload: Input payload
        symptom_flags: Normalized symptom flags
    
    Returns:
        Dictionary of derived flags
    """
    flags = {}
    
    # Has images
    camera_inputs = payload.get("camera_inputs", {})
    if camera_inputs:
        flags["has_images"] = any([
            camera_inputs.get("conjunctiva_photo"),
            camera_inputs.get("swelling_photo"),
            camera_inputs.get("child_arm_photo"),
            camera_inputs.get("skin_photo"),
        ])
    else:
        flags["has_images"] = False
    
    # Maternal risk factors
    is_pregnant = payload.get("pregnant", False)
    vitals = payload.get("vitals", {})
    bp_sys = vitals.get("bp_systolic")
    bp_dia = vitals.get("bp_diastolic")
    
    flags["has_maternal_risk_factors"] = is_pregnant and (
        (bp_sys and bp_sys >= 140) or
        (bp_dia and bp_dia >= 90) or
        symptom_flags.get("headache", False) or
        symptom_flags.get("swelling", False) or
        symptom_flags.get("decreased_fetal_movement", False)
    )
    
    # Anemia symptoms
    flags["has_anemia_symptoms"] = (
        symptom_flags.get("fatigue", False) or
        symptom_flags.get("dizziness", False) or
        symptom_flags.get("breathlessness", False)
    )
    
    # Requires urgent care (preliminary check)
    flags["requires_urgent_care"] = (
        (bp_sys and bp_sys >= 160) or
        (bp_dia and bp_dia >= 100) or
        symptom_flags.get("chest_pain", False) or
        symptom_flags.get("decreased_fetal_movement", False)
    )
    
    return flags
