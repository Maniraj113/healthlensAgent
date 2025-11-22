"""Risk calculator that orchestrates medical rule engine"""

from typing import Tuple
from .medical_rules import MedicalRuleEngine
from ..models.input_models import NormalizedContext
from ..models.output_models import (
    RiskScores,
    TriageLevel,
    ReasoningResult,
    ImageEvidence,
)


class RiskCalculator:
    """
    High-level risk calculator that uses MedicalRuleEngine
    to compute all risk scores and triage level.
    """
    
    def __init__(self):
        self.rule_engine = MedicalRuleEngine()
    
    def calculate_all_risks(
        self,
        context: NormalizedContext,
        image_evidence: ImageEvidence
    ) -> ReasoningResult:
        """
        Calculate all risk scores and determine triage level.
        
        Args:
            context: Normalized patient context
            image_evidence: Evidence from image analysis
        
        Returns:
            ReasoningResult with all scores, triage level, and reasoning trace
        """
        # Reset reasoning trace
        self.rule_engine.reset_trace()
        
        # Calculate individual risk scores
        anemia_risk = self.rule_engine.calculate_anemia_risk(context, image_evidence)
        maternal_risk = self.rule_engine.calculate_maternal_risk(context, image_evidence)
        sugar_risk = self.rule_engine.calculate_sugar_risk(context)
        nutrition_risk = self.rule_engine.calculate_nutrition_risk(context, image_evidence)
        infection_risk = self.rule_engine.calculate_infection_risk(context, image_evidence)
        
        # Combine into RiskScores
        risk_scores = RiskScores(
            anemia=anemia_risk,
            maternal=maternal_risk,
            sugar=sugar_risk,
            nutrition=nutrition_risk,
            infection=infection_risk,
        )
        
        # Determine triage level
        triage_level = self.rule_engine.determine_triage_level(risk_scores)
        
        # Identify primary concern
        primary_concern = self.rule_engine.identify_primary_concern(risk_scores)
        
        # Get reasoning trace
        reasoning_trace = self.rule_engine.reasoning_trace
        
        return ReasoningResult(
            risk_scores=risk_scores,
            triage_level=triage_level,
            reasoning_trace=reasoning_trace,
            primary_concern=primary_concern,
        )
