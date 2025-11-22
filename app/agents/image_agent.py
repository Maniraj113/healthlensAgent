"""Image Interpretation Agent - Analyzes medical images"""

from google.adk.agents import LlmAgent
from typing import Dict, Any, Optional
import logging

from ..tools.image_tools import (
    analyze_conjunctiva_image,
    analyze_swelling_image,
    analyze_child_arm_image,
    analyze_skin_image,
    create_image_evidence_dict,
)


logger = logging.getLogger(__name__)


def process_medical_images(
    conjunctiva_photo: Optional[str] = None,
    swelling_photo: Optional[str] = None,
    child_arm_photo: Optional[str] = None,
    skin_photo: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Tool: Process all available medical images and extract evidence.
    
    Analyzes conjunctiva for anemia, swelling for edema, child arm for malnutrition,
    and skin for infection/dehydration.
    
    Args:
        conjunctiva_photo: Base64 encoded conjunctiva image
        swelling_photo: Base64 encoded swelling image
        child_arm_photo: Base64 encoded child arm image
        skin_photo: Base64 encoded skin image
    
    Returns:
        Dictionary with image evidence (pallor, edema, malnutrition, infection, dehydration)
    """
    logger.info("Image Agent: Starting medical image processing")
    
    conjunctiva_result = None
    swelling_result = None
    child_arm_result = None
    skin_result = None
    
    # Analyze each image if provided
    if conjunctiva_photo:
        conjunctiva_result = analyze_conjunctiva_image(conjunctiva_photo)
    
    if swelling_photo:
        swelling_result = analyze_swelling_image(swelling_photo)
    
    if child_arm_photo:
        child_arm_result = analyze_child_arm_image(child_arm_photo)
    
    if skin_photo:
        skin_result = analyze_skin_image(skin_photo)
    
    # Create evidence dictionary
    evidence = create_image_evidence_dict(
        conjunctiva_result=conjunctiva_result,
        swelling_result=swelling_result,
        child_arm_result=child_arm_result,
        skin_result=skin_result,
    )
    
    logger.info("Image Agent: Image processing complete")
    
    return evidence


def create_image_agent() -> LlmAgent:
    """
    Create the Image Interpretation Agent.
    
    Purpose:
    - Analyze conjunctiva, swelling, and child arm photos
    - Output binary cues + confidence scores
    - Detect pallor, edema, malnutrition, infection, dehydration
    
    Returns:
        Configured LlmAgent for image interpretation
    """
    agent = LlmAgent(
        model="gemini-2.0-flash-exp",
        name="image_agent",
        instruction="""You are the Image Interpretation Agent for a health triage system.

Your responsibilities:
1. Receive camera inputs (base64 encoded images) from the normalized context
2. Use the process_medical_images tool to analyze all available images
3. Extract medical evidence:
   - Pallor (anemia) from conjunctiva photo
   - Edema (swelling) from swelling photo
   - Malnutrition from child arm photo
   - Skin infection and dehydration from skin photo
4. Return image_evidence dictionary with binary flags and confidence scores

IMPORTANT:
- Only process images that are actually provided (not None)
- Each detection includes a confidence score (0.0 to 1.0)
- Return structured evidence that will be used by the Clinical Reasoning Agent
- If no images are provided, return all flags as False with 0.0 confidence

Use the process_medical_images tool with the available image inputs.
""",
        description="Analyzes medical images to extract clinical evidence",
        tools=[process_medical_images],
    )
    
    return agent
