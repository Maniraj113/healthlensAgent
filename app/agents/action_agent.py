"""Action Planner / Communicator Agent - Generates patient-facing advice"""

from google.adk.agents import LlmAgent
from typing import Dict, Any
import logging

from ..core.nlg_templates import NLGTemplates
from ..models.output_models import ReasoningResult


logger = logging.getLogger(__name__)


def generate_patient_communication(
    reasoning_result: Dict[str, Any],
    language: str = "english"
) -> Dict[str, Any]:
    """
    Tool: Generate natural language summary and action plan.
    
    Converts clinical reasoning results into plain-language advice
    in the patient's preferred language.
    
    Args:
        reasoning_result: Clinical reasoning output with risk scores
        language: Target language (english, hindi, tamil, telugu, bengali)
    
    Returns:
        ActionPlan dictionary with summary, checklist, emergency signs, voice text
    """
    logger.info(f"Action Agent: Generating patient communication in {language}")
    
    # Convert to ReasoningResult model
    result = ReasoningResult(**reasoning_result)
    
    # Use NLG templates
    nlg = NLGTemplates()
    action_plan = nlg.generate_action_plan(result, language)
    
    # Convert to dictionary
    plan_dict = action_plan.model_dump()
    logger.info("Action Agent: Communication generation complete")
    
    return plan_dict


def create_action_agent() -> LlmAgent:
    """
    Create the Action Planner / Communicator Agent.
    
    Purpose:
    - Convert risk scores into plain-language advice
    - Generate summary_text, action_checklist, emergency_signs
    - Produce voice_text for TTS
    - Localize text in chosen language
    
    Returns:
        Configured LlmAgent for action planning
    """
    agent = LlmAgent(
        model="gemini-2.0-flash-exp",
        name="action_agent",
        instruction="""You are the Action Planner and Communicator Agent for a health triage system.

Your responsibilities:
1. Receive reasoning_result from Clinical Reasoning Agent
2. Receive the patient's preferred language
3. Use the generate_patient_communication tool to create:
   - summary_text: Plain language summary of health status
   - action_checklist: Specific actionable steps for the health worker
   - emergency_signs: Warning signs to watch for
   - voice_text: Simplified text for text-to-speech output
4. All text is localized to the patient's language (English, Hindi, Tamil, Telugu, Bengali)

The output should be:
- Clear and actionable for frontline health workers with limited medical training
- Culturally appropriate for rural Indian context
- Specific about urgency and next steps
- Include emergency warning signs when relevant

Use the generate_patient_communication tool with the reasoning_result and language.
Return the complete action_plan.
""",
        description="Generates multilingual patient-facing advice and action plans",
        tools=[generate_patient_communication],
    )
    
    return agent
