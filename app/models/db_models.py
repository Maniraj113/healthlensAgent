"""Database models using SQLModel"""

from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime


class VisitBase(SQLModel):
    """Base visit model"""
    patient_id: str = Field(index=True)
    worker_id: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Store complete payload as JSON
    input_payload: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    # Store results as JSON
    risk_scores: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    image_evidence: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    reasoning_trace: list = Field(default_factory=list, sa_column=Column(JSON))
    
    # Computed fields
    triage_level: str
    primary_concern: Optional[str] = None
    
    # Action plan
    summary_text: str
    action_checklist: list = Field(default_factory=list, sa_column=Column(JSON))
    voice_text: str
    language: str = "english"
    
    # Status
    offline_processed: bool = False
    synced: bool = False


class Visit(VisitBase, table=True):
    """Visit database table"""
    __tablename__ = "visits"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    visit_id: str = Field(unique=True, index=True)


class VisitCreate(VisitBase):
    """Model for creating a visit"""
    visit_id: str
