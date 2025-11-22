"""Database tools for storing and retrieving visit records"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from ..models.db_models import Visit, VisitCreate
from ..database.session import engine


def store_visit_record(visit_data: Dict[str, Any]) -> str:
    """
    Store a visit record in the database.
    
    Args:
        visit_data: Dictionary containing visit information
    
    Returns:
        visit_id of the stored record
    """
    try:
        with Session(engine) as session:
            # Create Visit object
            visit = Visit(**visit_data)
            session.add(visit)
            session.commit()
            session.refresh(visit)
            return visit.visit_id
    except Exception as e:
        print(f"Error storing visit record: {e}")
        raise


def retrieve_visit_record(visit_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a visit record from the database.
    
    Args:
        visit_id: Unique visit identifier
    
    Returns:
        Dictionary containing visit data or None if not found
    """
    try:
        with Session(engine) as session:
            statement = select(Visit).where(Visit.visit_id == visit_id)
            visit = session.exec(statement).first()
            
            if visit:
                return visit.model_dump()
            return None
    except Exception as e:
        print(f"Error retrieving visit record: {e}")
        return None


def update_visit_sync_status(visit_id: str, synced: bool = True) -> bool:
    """
    Update the sync status of a visit.
    
    Args:
        visit_id: Unique visit identifier
        synced: Sync status to set
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with Session(engine) as session:
            statement = select(Visit).where(Visit.visit_id == visit_id)
            visit = session.exec(statement).first()
            
            if visit:
                visit.synced = synced
                session.add(visit)
                session.commit()
                return True
            return False
    except Exception as e:
        print(f"Error updating sync status: {e}")
        return False


def get_unsynced_visits(worker_id: Optional[str] = None) -> list:
    """
    Get all unsynced visits, optionally filtered by worker.
    
    Args:
        worker_id: Optional worker ID to filter by
    
    Returns:
        List of unsynced visit dictionaries
    """
    try:
        with Session(engine) as session:
            statement = select(Visit).where(Visit.synced == False)
            
            if worker_id:
                statement = statement.where(Visit.worker_id == worker_id)
            
            visits = session.exec(statement).all()
            return [visit.model_dump() for visit in visits]
    except Exception as e:
        print(f"Error retrieving unsynced visits: {e}")
        return []
