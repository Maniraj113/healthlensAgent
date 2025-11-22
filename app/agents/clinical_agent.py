"""Clinical Reasoning Agent - Computes risk scores and triage level"""

from google.adk.agents import LlmAgent
from typing import Dict, Any

from ..core.risk_calculator import RiskCalculator
from ..models.input_models import NormalizedContext
from ..models.output_models import ImageEvidence


def calculate_risk_scores(
    normalized_context: Dict[str, Any],
    image_evidence: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Tool: Calculate all risk scores using medical rule engine.
    
    Applies clinical decision rules to compute:
    - Anemia risk
    - Maternal risk
    - Sugar/diabetes risk
    - Nutrition risk
    - Infection risk
    
    Also determines triage level and primary concern.
    
    Args:
        normalized_context: Normalized patient context
        image_evidence: Evidence from image analysis
    
    Returns:
        ReasoningResult dictionary with risk scores, triage level, and reasoning trace
    """
    # Convert dicts to Pydantic models
    context = NormalizedContext(**normalized_context)
    evidence = ImageEvidence(**image_evidence)
    
    # Use RiskCalculator
    calculator = RiskCalculator()
    reasoning_result = calculator.calculate_all_risks(context, evidence)
    
    # Convert to dictionary
    return reasoning_result.model_dump()


def create_clinical_agent() -> LlmAgent:
    """
    Create the Clinical Reasoning Agent.
    
    Purpose:
    - Combine normalized_context + image_evidence
    - Apply medical rule engine
    - Compute domain risk scores (anemia, maternal, sugar, infection, nutrition)
    - Assign triage level (low, moderate, high, urgent)
    - Generate reasoning trace (list of rules fired + evidence)
    
    Returns:
        Configured LlmAgent for clinical reasoning
    """
    agent = LlmAgent(
        model="gemini-2.0-flash-exp",
        name="clinical_agent",
        instruction="""You are the Clinical Reasoning Agent for a health triage system.

Your responsibilities:
1. Receive normalized_context from Intake Agent
2. Receive image_evidence from Image Agent
3. Use the calculate_risk_scores tool to apply medical decision rules
4. The tool will compute:
   - Anemia risk score and level
   - Maternal risk score and level
   - Sugar/diabetes risk score and level
   - Nutrition risk score and level
   - Infection risk score and level
   - Overall triage level (low/moderate/high/urgent)
   - Primary health concern
   - Detailed reasoning trace showing which rules fired

The medical rules are based on:
- WHO guidelines
- Indian NRHM protocols for frontline health workers
- Evidence-based clinical decision support

Return the complete reasoning_result with all risk scores and reasoning trace.
This will be used by the Action Planner Agent to generate patient-facing advice.
""",
        description="Applies medical rules to compute risk scores and triage level",
        tools=[calculate_risk_scores],
    )
    
    return agent
