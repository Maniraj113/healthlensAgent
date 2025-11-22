"""Medical rule engine for clinical reasoning"""

from typing import List, Dict, Any, Tuple
import logging
from ..models.input_models import NormalizedContext
from ..models.output_models import (
    RiskScore,
    RiskScores,
    RiskLevel,
    TriageLevel,
    ReasoningFact,
    ImageEvidence,
)

logger = logging.getLogger(__name__)


class MedicalRuleEngine:
    """
    Implements clinical decision rules for health risk assessment.
    Based on WHO and Indian NRHM guidelines for frontline workers.
    """
    
    def __init__(self):
        self.reasoning_trace: List[ReasoningFact] = []
    
    def reset_trace(self):
        """Reset reasoning trace for new analysis"""
        self.reasoning_trace = []
    
    def add_fact(self, fact: str, weight: int, confidence: float = 1.0):
        """Add a reasoning fact to the trace"""
        self.reasoning_trace.append(
            ReasoningFact(fact=fact, weight=weight, confidence=confidence)
        )
        # Log each rule that fires
        logger.info(f"      🔹 Rule fired: {fact} [weight: {weight}, confidence: {confidence:.2f}]")
    
    def calculate_anemia_risk(
        self,
        context: NormalizedContext,
        image_evidence: ImageEvidence
    ) -> RiskScore:
        """
        Calculate anemia risk score.
        
        Rules:
        - Pallor detected: +40
        - Heart rate > 100: +10
        - Fatigue symptom: +10
        - Dizziness: +5
        - Breathlessness: +10
        - Pregnant: multiply by 1.2
        
        Levels:
        - 0-30: low
        - 31-60: moderate
        - >60: high
        """
        score = 0
        
        # Image evidence
        if image_evidence.pallor:
            weight = 40
            score += weight
            self.add_fact(
                f"Pallor detected in conjunctiva",
                weight,
                image_evidence.pallor_confidence
            )
        
        # Vital signs
        if context.normalized_heart_rate and context.normalized_heart_rate > 100:
            weight = 10
            score += weight
            self.add_fact(f"Elevated heart rate: {context.normalized_heart_rate} bpm", weight)
        
        # Symptoms
        if context.symptom_flags.get("fatigue", False):
            weight = 10
            score += weight
            self.add_fact("Fatigue reported", weight)
        
        if context.symptom_flags.get("dizziness", False):
            weight = 5
            score += weight
            self.add_fact("Dizziness reported", weight)
        
        if context.symptom_flags.get("breathlessness", False):
            weight = 10
            score += weight
            self.add_fact("Breathlessness reported", weight)
        
        # Pregnancy multiplier
        if context.payload.pregnant:
            original_score = score
            score = int(score * 1.2)
            self.add_fact(
                f"Pregnancy risk multiplier applied (x1.2): {original_score} → {score}",
                score - original_score
            )
        
        # Determine level
        if score <= 30:
            level = RiskLevel.low
        elif score <= 60:
            level = RiskLevel.moderate
        else:
            level = RiskLevel.high
        
        return RiskScore(score=min(score, 100), level=level)
    
    def calculate_maternal_risk(
        self,
        context: NormalizedContext,
        image_evidence: ImageEvidence
    ) -> RiskScore:
        """
        Calculate maternal risk score.
        
        Rules:
        - BP >= 140/90: +60
        - Edema visible: +20
        - Headache: +10
        - Decreased fetal movement: +30
        - Abdominal pain: +15
        - Fever: +10
        
        Levels:
        - 0-40: low
        - 41-70: moderate
        - >70: high/urgent
        """
        score = 0
        
        # Not applicable if not pregnant
        if not context.payload.pregnant:
            return RiskScore(score=0, level=RiskLevel.low)
        
        # Blood pressure
        bp_sys = context.normalized_bp_systolic
        bp_dia = context.normalized_bp_diastolic
        
        if bp_sys and bp_dia:
            if bp_sys >= 140 or bp_dia >= 90:
                weight = 60
                score += weight
                self.add_fact(f"Elevated BP: {bp_sys}/{bp_dia} mmHg", weight, 0.98)
        
        # Edema from image
        if image_evidence.edema_detected:
            weight = 20
            score += weight
            self.add_fact(
                "Edema/swelling detected",
                weight,
                image_evidence.edema_confidence
            )
        
        # Symptoms
        if context.symptom_flags.get("headache", False):
            weight = 10
            score += weight
            self.add_fact("Headache reported", weight)
        
        if context.symptom_flags.get("decreased_fetal_movement", False):
            weight = 30
            score += weight
            self.add_fact("Decreased fetal movement reported", weight, 0.95)
        
        if context.symptom_flags.get("abdominal_pain", False):
            weight = 15
            score += weight
            self.add_fact("Abdominal pain reported", weight)
        
        if context.symptom_flags.get("fever", False):
            weight = 10
            score += weight
            self.add_fact("Fever reported", weight)
        
        # Determine level
        if score <= 40:
            level = RiskLevel.low
        elif score <= 70:
            level = RiskLevel.moderate
        else:
            level = RiskLevel.urgent
        
        return RiskScore(score=min(score, 100), level=level)
    
    def calculate_sugar_risk(self, context: NormalizedContext) -> RiskScore:
        """
        Calculate diabetes/sugar risk.
        
        Rules:
        - Glucose >= 200: high
        - Glucose 140-199: moderate
        - Glucose < 140: low
        """
        score = 0
        glucose = context.normalized_glucose
        
        if glucose is None:
            return RiskScore(score=0, level=RiskLevel.low)
        
        if glucose >= 200:
            score = 80
            level = RiskLevel.high
            self.add_fact(f"High random glucose: {glucose} mg/dL", 80, 0.98)
        elif glucose >= 140:
            score = 50
            level = RiskLevel.moderate
            self.add_fact(f"Elevated random glucose: {glucose} mg/dL", 50, 0.95)
        else:
            score = 10
            level = RiskLevel.low
            self.add_fact(f"Normal random glucose: {glucose} mg/dL", 0, 0.98)
        
        return RiskScore(score=score, level=level)
    
    def calculate_nutrition_risk(
        self,
        context: NormalizedContext,
        image_evidence: ImageEvidence
    ) -> RiskScore:
        """
        Calculate malnutrition risk (primarily for children).
        
        Rules:
        - Malnutrition flag from image: moderate/high
        - Age < 5 with low weight indicators: high
        """
        score = 0
        
        if image_evidence.malnutrition_flag:
            score = 70
            level = RiskLevel.high
            self.add_fact(
                "Malnutrition indicators detected in arm circumference",
                70,
                image_evidence.malnutrition_confidence
            )
        else:
            score = 10
            level = RiskLevel.low
        
        return RiskScore(score=score, level=level)
    
    def calculate_infection_risk(
        self,
        context: NormalizedContext,
        image_evidence: ImageEvidence
    ) -> RiskScore:
        """
        Calculate infection risk.
        
        Rules:
        - Fever + cough: +30
        - Skin infection detected: +40
        - Temperature > 38.5°C: +20
        """
        score = 0
        
        # Temperature
        temp = context.payload.vitals.temperature_c
        if temp and temp > 38.5:
            weight = 20
            score += weight
            self.add_fact(f"High fever: {temp}°C", weight)
        
        # Symptoms
        has_fever = context.symptom_flags.get("fever", False)
        has_cough = context.symptom_flags.get("cough", False)
        
        if has_fever and has_cough:
            weight = 30
            score += weight
            self.add_fact("Fever with cough (respiratory infection)", weight)
        
        # Skin infection from image
        if image_evidence.skin_infection:
            weight = 40
            score += weight
            self.add_fact(
                "Skin infection detected",
                weight,
                image_evidence.skin_infection_confidence
            )
        
        # Determine level
        if score <= 30:
            level = RiskLevel.low
        elif score <= 60:
            level = RiskLevel.moderate
        else:
            level = RiskLevel.high
        
        return RiskScore(score=score, level=level)
    
    def determine_triage_level(self, risk_scores: RiskScores) -> TriageLevel:
        """
        Determine overall triage level based on highest risk.
        
        Priority: maternal > anemia > infection > sugar > nutrition
        """
        # Maternal risk takes highest priority
        if risk_scores.maternal.level == RiskLevel.urgent:
            return TriageLevel.urgent
        if risk_scores.maternal.level == RiskLevel.high:
            return TriageLevel.high
        
        # Check other high risks
        high_risks = []
        if risk_scores.anemia.level == RiskLevel.high:
            high_risks.append("anemia")
        if risk_scores.sugar.level == RiskLevel.high:
            high_risks.append("sugar")
        if risk_scores.infection and risk_scores.infection.level == RiskLevel.high:
            high_risks.append("infection")
        if risk_scores.nutrition and risk_scores.nutrition.level == RiskLevel.high:
            high_risks.append("nutrition")
        
        if high_risks:
            return TriageLevel.high
        
        # Check moderate risks
        moderate_risks = []
        if risk_scores.maternal.level == RiskLevel.moderate:
            moderate_risks.append("maternal")
        if risk_scores.anemia.level == RiskLevel.moderate:
            moderate_risks.append("anemia")
        if risk_scores.sugar.level == RiskLevel.moderate:
            moderate_risks.append("sugar")
        if risk_scores.infection and risk_scores.infection.level == RiskLevel.moderate:
            moderate_risks.append("infection")
        if risk_scores.nutrition and risk_scores.nutrition.level == RiskLevel.moderate:
            moderate_risks.append("nutrition")
        
        if moderate_risks:
            return TriageLevel.moderate
        
        return TriageLevel.low
    
    def identify_primary_concern(self, risk_scores: RiskScores) -> str:
        """Identify the primary health concern"""
        
        # Maternal takes priority
        if risk_scores.maternal.score > 40:
            if risk_scores.maternal.score >= 70:
                return "maternal_hypertension_urgent"
            return "maternal_risk"
        
        # Find highest score
        max_score = 0
        primary = "general_health"
        
        if risk_scores.anemia.score > max_score:
            max_score = risk_scores.anemia.score
            primary = "anemia"
        
        if risk_scores.sugar.score > max_score:
            max_score = risk_scores.sugar.score
            primary = "diabetes"
        
        if risk_scores.infection and risk_scores.infection.score > max_score:
            max_score = risk_scores.infection.score
            primary = "infection"
        
        if risk_scores.nutrition and risk_scores.nutrition.score > max_score:
            max_score = risk_scores.nutrition.score
            primary = "malnutrition"
        
        return primary
