"""Image analysis tools for Image Interpretation Agent"""

import base64
import io
from typing import Tuple, Optional
from PIL import Image
import numpy as np


def decode_base64_image(base64_string: str) -> Optional[Image.Image]:
    """
    Decode base64 string to PIL Image.
    
    Args:
        base64_string: Base64 encoded image string
    
    Returns:
        PIL Image object or None if decoding fails
    """
    try:
        # Remove data URL prefix if present
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        
        # Decode base64
        image_bytes = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_bytes))
        return image
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None


def analyze_conjunctiva_image(base64_image: str) -> Tuple[bool, float]:
    """
    Analyze conjunctiva image for pallor (anemia indicator).
    
    This is a STUB implementation for MVP. In production, this would:
    - Use a trained vision model (e.g., fine-tuned Gemini Vision)
    - Analyze color intensity in conjunctiva region
    - Compare against normal color ranges
    
    Args:
        base64_image: Base64 encoded conjunctiva photo
    
    Returns:
        Tuple of (pallor_detected: bool, confidence: float)
    """
    image = decode_base64_image(base64_image)
    
    if image is None:
        return False, 0.0
    
    # STUB: Simple heuristic based on average redness
    # In production, replace with actual ML model
    try:
        # Convert to RGB
        image = image.convert("RGB")
        img_array = np.array(image)
        
        # Calculate average red channel intensity
        red_channel = img_array[:, :, 0]
        avg_red = np.mean(red_channel)
        
        # Simple threshold: if average red < 120, consider pallor
        # This is a PLACEHOLDER - real model would be much more sophisticated
        pallor_detected = avg_red < 120
        
        # Mock confidence based on how far from threshold
        confidence = min(abs(120 - avg_red) / 120, 1.0)
        confidence = max(confidence, 0.5)  # Minimum confidence
        
        return pallor_detected, float(confidence)
    
    except Exception as e:
        print(f"Error analyzing conjunctiva image: {e}")
        return False, 0.0


def analyze_swelling_image(base64_image: str) -> Tuple[bool, float]:
    """
    Analyze image for edema/swelling (maternal risk indicator).
    
    STUB implementation. Production version would:
    - Detect skin texture changes
    - Identify pitting edema patterns
    - Measure swelling extent
    
    Args:
        base64_image: Base64 encoded swelling photo
    
    Returns:
        Tuple of (edema_detected: bool, confidence: float)
    """
    image = decode_base64_image(base64_image)
    
    if image is None:
        return False, 0.0
    
    # STUB: Mock detection
    # In production, use trained model for edema detection
    try:
        image = image.convert("RGB")
        img_array = np.array(image)
        
        # Mock heuristic: check for uniform color (swelling reduces texture)
        # Calculate standard deviation of grayscale
        gray = np.mean(img_array, axis=2)
        texture_variance = np.std(gray)
        
        # Low variance might indicate swelling (smooth, uniform surface)
        edema_detected = texture_variance < 30
        confidence = 0.75 if edema_detected else 0.25
        
        return edema_detected, float(confidence)
    
    except Exception as e:
        print(f"Error analyzing swelling image: {e}")
        return False, 0.0


def analyze_child_arm_image(base64_image: str) -> Tuple[bool, float]:
    """
    Analyze child's arm for malnutrition indicators (MUAC - Mid-Upper Arm Circumference).
    
    STUB implementation. Production version would:
    - Detect arm circumference using reference markers
    - Compare against WHO growth standards
    - Classify malnutrition severity
    
    Args:
        base64_image: Base64 encoded child arm photo
    
    Returns:
        Tuple of (malnutrition_flag: bool, confidence: float)
    """
    image = decode_base64_image(base64_image)
    
    if image is None:
        return False, 0.0
    
    # STUB: Mock detection
    # In production, use computer vision to measure arm circumference
    try:
        image = image.convert("RGB")
        img_array = np.array(image)
        
        # Mock heuristic: very simple placeholder
        # Real implementation would measure actual circumference
        height, width = img_array.shape[:2]
        
        # Arbitrary mock logic
        malnutrition_flag = False
        confidence = 0.3
        
        return malnutrition_flag, float(confidence)
    
    except Exception as e:
        print(f"Error analyzing child arm image: {e}")
        return False, 0.0


def analyze_skin_image(base64_image: str) -> Tuple[bool, bool, float, float]:
    """
    Analyze skin image for infection and dehydration signs.
    
    STUB implementation. Production version would:
    - Detect redness, lesions, rashes
    - Identify skin turgor (dehydration)
    - Classify infection types
    
    Args:
        base64_image: Base64 encoded skin photo
    
    Returns:
        Tuple of (infection_detected, dehydration_detected, infection_conf, dehydration_conf)
    """
    image = decode_base64_image(base64_image)
    
    if image is None:
        return False, False, 0.0, 0.0
    
    # STUB: Mock detection
    try:
        image = image.convert("RGB")
        img_array = np.array(image)
        
        # Mock heuristic for infection: high red channel
        red_channel = img_array[:, :, 0]
        avg_red = np.mean(red_channel)
        
        infection_detected = avg_red > 150
        infection_confidence = 0.6 if infection_detected else 0.2
        
        # Mock heuristic for dehydration: low overall brightness
        brightness = np.mean(img_array)
        dehydration_detected = brightness < 100
        dehydration_confidence = 0.5 if dehydration_detected else 0.2
        
        return infection_detected, dehydration_detected, float(infection_confidence), float(dehydration_confidence)
    
    except Exception as e:
        print(f"Error analyzing skin image: {e}")
        return False, False, 0.0, 0.0


def create_image_evidence_dict(
    conjunctiva_result: Optional[Tuple[bool, float]] = None,
    swelling_result: Optional[Tuple[bool, float]] = None,
    child_arm_result: Optional[Tuple[bool, float]] = None,
    skin_result: Optional[Tuple[bool, bool, float, float]] = None,
) -> dict:
    """
    Create image evidence dictionary from analysis results.
    
    Args:
        conjunctiva_result: (pallor, confidence)
        swelling_result: (edema, confidence)
        child_arm_result: (malnutrition, confidence)
        skin_result: (infection, dehydration, inf_conf, dehyd_conf)
    
    Returns:
        Dictionary matching ImageEvidence model
    """
    evidence = {
        "pallor": False,
        "pallor_confidence": 0.0,
        "edema_detected": False,
        "edema_confidence": 0.0,
        "malnutrition_flag": False,
        "malnutrition_confidence": 0.0,
        "skin_infection": False,
        "skin_infection_confidence": 0.0,
        "dehydration": False,
        "dehydration_confidence": 0.0,
    }
    
    if conjunctiva_result:
        evidence["pallor"] = conjunctiva_result[0]
        evidence["pallor_confidence"] = conjunctiva_result[1]
    
    if swelling_result:
        evidence["edema_detected"] = swelling_result[0]
        evidence["edema_confidence"] = swelling_result[1]
    
    if child_arm_result:
        evidence["malnutrition_flag"] = child_arm_result[0]
        evidence["malnutrition_confidence"] = child_arm_result[1]
    
    if skin_result:
        evidence["skin_infection"] = skin_result[0]
        evidence["dehydration"] = skin_result[1]
        evidence["skin_infection_confidence"] = skin_result[2]
        evidence["dehydration_confidence"] = skin_result[3]
    
    return evidence
