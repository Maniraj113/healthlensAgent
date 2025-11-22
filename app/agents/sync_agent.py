"""Follow-Up / Sync Agent - Handles data persistence and synchronization"""

from google.adk.agents import LlmAgent
from typing import Dict, Any
import uuid
from datetime import datetime

from ..tools.db_tools import store_visit_record, update_visit_sync_status


def save_visit_to_database(
    visit_id: str,
    patient_id: str,
    worker_id: str,
    input_payload: Dict[str, Any],
    risk_scores: Dict[str, Any],
    image_evidence: Dict[str, Any],
    reasoning_trace: list,
    triage_level: str,
    primary_concern: str,
    summary_text: str,
    action_checklist: list,
    voice_text: str,
    language: str,
    offline_processed: bool = False
) -> Dict[str, str]:
    """
    Tool: Save complete visit record to database.
    
    Stores all visit data including input, analysis results, and action plan.
    
    Args:
        visit_id: Unique visit identifier
        patient_id: Patient identifier
        worker_id: Health worker identifier
        input_payload: Original input data
        risk_scores: Computed risk scores
        image_evidence: Image analysis results
        reasoning_trace: Clinical reasoning steps
        triage_level: Overall triage level
        primary_concern: Primary health concern identified
        summary_text: Patient-facing summary
        action_checklist: Action steps
        voice_text: TTS text
        language: Language used
        offline_processed: Whether processed offline
    
    Returns:
        Status dictionary with visit_id and sync status
    """
    visit_data = {
        "visit_id": visit_id,
        "patient_id": patient_id,
        "worker_id": worker_id,
        "timestamp": datetime.utcnow(),
        "input_payload": input_payload,
        "risk_scores": risk_scores,
        "image_evidence": image_evidence,
        "reasoning_trace": reasoning_trace,
        "triage_level": triage_level,
        "primary_concern": primary_concern,
        "summary_text": summary_text,
        "action_checklist": action_checklist,
        "voice_text": voice_text,
        "language": language,
        "offline_processed": offline_processed,
        "synced": True,
    }
    
    try:
        stored_visit_id = store_visit_record(visit_data)
        return {
            "status": "success",
            "visit_id": stored_visit_id,
            "synced": True,
            "message": "Visit record saved successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "visit_id": visit_id,
            "synced": False,
            "message": f"Error saving visit: {str(e)}"
        }


def mark_visit_synced(visit_id: str) -> Dict[str, str]:
    """
    Tool: Mark a visit as synced.
    
    Updates the sync status of a visit record.
    
    Args:
        visit_id: Visit identifier to mark as synced
    
    Returns:
        Status dictionary
    """
    success = update_visit_sync_status(visit_id, synced=True)
    
    if success:
        return {
            "status": "success",
            "visit_id": visit_id,
            "message": "Visit marked as synced"
        }
    else:
        return {
            "status": "error",
            "visit_id": visit_id,
            "message": "Failed to update sync status"
        }


def create_sync_agent() -> LlmAgent:
    """
    Create the Follow-Up / Sync Agent.
    
    Purpose:
    - Store final authoritative result in database when network available
    - Mark visit as complete
    - Support "pull latest result" for React app
    - Handle offline-to-online synchronization
    
    Returns:
        Configured LlmAgent for data synchronization
    """
    agent = LlmAgent(
        model="gemini-2.0-flash-exp",
        name="sync_agent",
        instruction="""You are the Follow-Up and Sync Agent for a health triage system.

Your responsibilities:
1. Receive the complete visit data including:
   - Input payload
   - Risk scores and reasoning
   - Action plan
   - All metadata
2. Use save_visit_to_database tool to persist the visit record
3. Generate a unique visit_id if not already provided
4. Mark the visit as synced
5. Return sync status

This agent ensures that:
- All visit data is stored for future reference
- Health workers can retrieve past visits
- Offline visits can be synced when network becomes available
- Audit trail is maintained for quality assurance

Use the save_visit_to_database tool with all the visit information.
Return the sync_status indicating success or failure.
""",
        description="Persists visit data and handles synchronization",
        tools=[save_visit_to_database, mark_visit_synced],
    )
    
    return agent
