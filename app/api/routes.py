"""FastAPI routes for health triage API"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any

from ..models.input_models import InputPayload
from ..models.output_models import FinalResult
from ..orchestration import create_triage_workflow
from ..tools.db_tools import retrieve_visit_record, get_unsynced_visits

router = APIRouter(prefix="/api/v1", tags=["triage"])


@router.post("/analyze", response_model=FinalResult, status_code=status.HTTP_200_OK)
async def analyze_patient(payload: InputPayload) -> FinalResult:
    """
    Analyze patient vitals, symptoms, and images to produce triage recommendations.
    
    This endpoint:
    1. Validates and normalizes input
    2. Analyzes medical images (if provided)
    3. Computes risk scores using clinical rules
    4. Generates multilingual action plan
    5. Stores results in database
    
    Args:
        payload: Complete patient input including vitals, symptoms, images, metadata
    
    Returns:
        FinalResult with risk scores, triage level, summary, and action plan
    
    Raises:
        HTTPException: If workflow execution fails
    """
    try:
        # Create workflow
        workflow = create_triage_workflow()
        
        # Convert payload to dict
        payload_dict = payload.model_dump()
        
        # Run workflow
        result = await workflow.run_workflow(payload_dict)
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing triage request: {str(e)}"
        )


@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_offline_visits(visits: List[InputPayload]) -> Dict[str, Any]:
    """
    Sync multiple offline visits to the server.
    
    This endpoint processes visits that were created in offline mode
    and runs the full analysis workflow on each.
    
    Args:
        visits: List of visit payloads to sync
    
    Returns:
        Dictionary with sync results for each visit
    """
    results = []
    workflow = create_triage_workflow()
    
    for visit_payload in visits:
        try:
            # Force online processing
            payload_dict = visit_payload.model_dump()
            payload_dict["offline_mode"] = False
            
            # Run workflow
            result = await workflow.run_workflow(payload_dict)
            
            results.append({
                "visit_id": result.visit_id,
                "status": "success",
                "triage_level": result.triage_level,
            })
        
        except Exception as e:
            results.append({
                "patient_id": visit_payload.patient_id,
                "status": "error",
                "error": str(e),
            })
    
    return {
        "total": len(visits),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results,
    }


@router.get("/visit/{visit_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_visit(visit_id: str) -> Dict[str, Any]:
    """
    Retrieve stored visit data by visit ID.
    
    Args:
        visit_id: Unique visit identifier
    
    Returns:
        Complete visit record including input, results, and action plan
    
    Raises:
        HTTPException: If visit not found
    """
    visit = retrieve_visit_record(visit_id)
    
    if visit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Visit {visit_id} not found"
        )
    
    return visit


@router.get("/visits/unsynced", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def get_unsynced(worker_id: str = None) -> List[Dict[str, Any]]:
    """
    Get all unsynced visits, optionally filtered by worker.
    
    Args:
        worker_id: Optional worker ID to filter results
    
    Returns:
        List of unsynced visit records
    """
    visits = get_unsynced_visits(worker_id)
    return visits


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Status message
    """
    return {
        "status": "healthy",
        "service": "health_triage_api",
        "version": "1.0.0"
    }
