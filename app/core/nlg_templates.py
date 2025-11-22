"""Natural Language Generation templates for multilingual output"""

from typing import List, Dict
from ..models.output_models import ReasoningResult, TriageLevel, ActionPlan


class NLGTemplates:
    """
    Generates natural language summaries and action plans
    in multiple languages based on clinical reasoning results.
    """
    
    # Summary templates by primary concern and language
    SUMMARY_TEMPLATES = {
        "maternal_hypertension_urgent": {
            "english": "URGENT: High maternal risk due to elevated blood pressure ({bp}). Immediate referral to PHC required.",
            "hindi": "तत्काल: उच्च रक्तचाप ({bp}) के कारण गर्भवती महिला को तुरंत PHC भेजें।",
            "tamil": "அவசரம்: உயர் இரத்த அழுத்தம் ({bp}) காரணமாக உடனடியாக PHC க்கு அனுப்பவும்.",
        },
        "maternal_risk": {
            "english": "Maternal health concern detected. Blood pressure: {bp}. Recommend PHC visit within 24 hours.",
            "hindi": "गर्भवती महिला के स्वास्थ्य में चिंता। रक्तचाप: {bp}। 24 घंटे में PHC जाएं।",
            "tamil": "கர்ப்பிணி பெண்ணின் உடல்நலம் கவனிக்கப்பட வேண்டும். இரத்த அழுத்தம்: {bp}। 24 மணி நேரத்தில் PHC செல்லவும்.",
        },
        "anemia": {
            "english": "Anemia risk detected. Symptoms include pallor and fatigue. Iron supplementation and PHC consultation recommended.",
            "hindi": "खून की कमी का खतरा। पीलापन और थकान। आयरन की गोलियां लें और PHC जाएं।",
            "tamil": "இரத்த சோகை அபாயம். வெளிறிய நிறம் மற்றும் சோர்வு. இரும்புச்சத்து மாத்திரைகள் மற்றும் PHC ஆலோசனை.",
        },
        "diabetes": {
            "english": "Elevated blood sugar detected ({glucose} mg/dL). Dietary modifications and PHC follow-up needed.",
            "hindi": "रक्त शर्करा बढ़ा हुआ ({glucose} mg/dL)। खान-पान में बदलाव और PHC जाएं।",
            "tamil": "உயர் இரத்த சர்க்கரை ({glucose} mg/dL). உணவு மாற்றங்கள் மற்றும் PHC பரிசோதனை.",
        },
        "infection": {
            "english": "Infection risk detected. Fever and symptoms present. Medical evaluation recommended.",
            "hindi": "संक्रमण का खतरा। बुखार और लक्षण। डॉक्टर से मिलें।",
            "tamil": "தொற்று அபாயம். காய்ச்சல் மற்றும் அறிகுறிகள். மருத்துவ பரிசோதனை தேவை.",
        },
        "malnutrition": {
            "english": "Malnutrition indicators detected. Nutritional supplementation and monitoring required.",
            "hindi": "कुपोषण के संकेत। पोषण पूरक और निगरानी आवश्यक।",
            "tamil": "ஊட்டச்சத்து குறைபாடு அறிகுறிகள். ஊட்டச்சத்து மற்றும் கண்காணிப்பு தேவை.",
        },
        "general_health": {
            "english": "General health assessment completed. Continue routine monitoring.",
            "hindi": "सामान्य स्वास्थ्य जांच पूर्ण। नियमित निगरानी जारी रखें।",
            "tamil": "பொது உடல்நல மதிப்பீடு முடிந்தது. வழக்கமான கண்காணிப்பு தொடரவும்.",
        }
    }
    
    # Action checklists by triage level
    ACTION_CHECKLISTS = {
        "urgent": {
            "english": [
                "Arrange immediate transport to Primary Health Center (PHC)",
                "Do NOT allow patient to walk or exert",
                "Accompany patient to PHC",
                "Inform PHC medical officer in advance",
                "Monitor vital signs during transport"
            ],
            "hindi": [
                "तुरंत PHC के लिए वाहन की व्यवस्था करें",
                "मरीज को चलने या मेहनत न करने दें",
                "मरीज के साथ PHC जाएं",
                "PHC के डॉक्टर को पहले से सूचित करें",
                "रास्ते में जीवन संकेतों की निगरानी करें"
            ],
            "tamil": [
                "உடனடியாக PHC க்கு போக்குவரத்து ஏற்பாடு செய்யவும்",
                "நோயாளி நடக்க அல்லது உழைக்க அனுமதிக்க வேண்டாம்",
                "நோயாளியுடன் PHC செல்லவும்",
                "PHC மருத்துவரை முன்கூட்டியே தெரிவிக்கவும்",
                "பயணத்தின் போது உயிர் அறிகுறிகளை கண்காணிக்கவும்"
            ]
        },
        "high": {
            "english": [
                "Schedule PHC visit within 24 hours",
                "Advise rest and avoid strenuous activity",
                "Monitor symptoms closely",
                "Provide written referral note",
                "Follow up within 2 days"
            ],
            "hindi": [
                "24 घंटे में PHC जाने का समय तय करें",
                "आराम करें और भारी काम न करें",
                "लक्षणों पर नजर रखें",
                "लिखित रेफरल नोट दें",
                "2 दिन में फॉलो-अप करें"
            ],
            "tamil": [
                "24 மணி நேரத்தில் PHC பார்வை திட்டமிடவும்",
                "ஓய்வு மற்றும் கடினமான செயல்பாடுகளை தவிர்க்கவும்",
                "அறிகுறிகளை நெருக்கமாக கண்காணிக்கவும்",
                "எழுத்துப்பூர்வ பரிந்துரை குறிப்பு வழங்கவும்",
                "2 நாட்களில் பின்தொடர்தல்"
            ]
        },
        "moderate": {
            "english": [
                "Schedule PHC visit within 3-5 days",
                "Continue monitoring at home",
                "Maintain symptom diary",
                "Follow dietary/medication advice",
                "Return if symptoms worsen"
            ],
            "hindi": [
                "3-5 दिन में PHC जाएं",
                "घर पर निगरानी जारी रखें",
                "लक्षणों की डायरी रखें",
                "आहार/दवा की सलाह मानें",
                "लक्षण बढ़ने पर वापस आएं"
            ],
            "tamil": [
                "3-5 நாட்களில் PHC பார்வை",
                "வீட்டில் கண்காணிப்பு தொடரவும்",
                "அறிகுறி நாட்குறிப்பு பராமரிக்கவும்",
                "உணவு/மருந்து ஆலோசனையை பின்பற்றவும்",
                "அறிகுறிகள் மோசமானால் திரும்பவும்"
            ]
        },
        "low": {
            "english": [
                "Continue routine health monitoring",
                "Maintain healthy diet and lifestyle",
                "Schedule next regular checkup",
                "Watch for any new symptoms",
                "Contact health worker if concerns arise"
            ],
            "hindi": [
                "नियमित स्वास्थ्य निगरानी जारी रखें",
                "स्वस्थ आहार और जीवनशैली बनाए रखें",
                "अगली नियमित जांच का समय तय करें",
                "नए लक्षणों पर ध्यान दें",
                "चिंता होने पर स्वास्थ्य कार्यकर्ता से संपर्क करें"
            ],
            "tamil": [
                "வழக்கமான உடல்நல கண்காணிப்பு தொடரவும்",
                "ஆரோக்கியமான உணவு மற்றும் வாழ்க்கை முறை பராமரிக்கவும்",
                "அடுத்த வழக்கமான பரிசோதனை திட்டமிடவும்",
                "புதிய அறிகுறிகளை கவனிக்கவும்",
                "கவலைகள் எழுந்தால் சுகாதார பணியாளரை தொடர்பு கொள்ளவும்"
            ]
        }
    }
    
    # Emergency warning signs
    EMERGENCY_SIGNS = {
        "maternal": {
            "english": [
                "Severe headache or vision changes",
                "Seizures or convulsions",
                "Severe abdominal pain",
                "Heavy vaginal bleeding",
                "Reduced or no fetal movement"
            ],
            "hindi": [
                "गंभीर सिरदर्द या दृष्टि में बदलाव",
                "दौरे या ऐंठन",
                "गंभीर पेट दर्द",
                "भारी योनि से रक्तस्राव",
                "भ्रूण की गति कम या नहीं"
            ],
            "tamil": [
                "கடுமையான தலைவலி அல்லது பார்வை மாற்றங்கள்",
                "வலிப்புத்தாக்கங்கள்",
                "கடுமையான வயிற்று வலி",
                "அதிக யோனி இரத்தப்போக்கு",
                "குறைந்த அல்லது கருவின் இயக்கம் இல்லை"
            ]
        },
        "anemia": {
            "english": [
                "Extreme weakness or fainting",
                "Rapid heartbeat at rest",
                "Severe breathlessness",
                "Chest pain"
            ],
            "hindi": [
                "अत्यधिक कमजोरी या बेहोशी",
                "आराम के समय तेज़ दिल की धड़कन",
                "गंभीर सांस फूलना",
                "सीने में दर्द"
            ],
            "tamil": [
                "தீவிர பலவீனம் அல்லது மயக்கம்",
                "ஓய்வில் விரைவான இதயத் துடிப்பு",
                "கடுமையான மூச்சுத் திணறல்",
                "மார்பு வலி"
            ]
        },
        "general": {
            "english": [
                "Difficulty breathing",
                "Persistent high fever",
                "Severe pain",
                "Confusion or altered consciousness"
            ],
            "hindi": [
                "सांस लेने में कठिनाई",
                "लगातार तेज बुखार",
                "गंभीर दर्द",
                "भ्रम या चेतना में बदलाव"
            ],
            "tamil": [
                "சுவாசிப்பதில் சிரமம்",
                "தொடர்ச்சியான அதிக காய்ச்சல்",
                "கடுமையான வலி",
                "குழப்பம் அல்லது மாற்றப்பட்ட உணர்வு"
            ]
        }
    }
    
    def generate_action_plan(
        self,
        reasoning_result: ReasoningResult,
        language: str = "english"
    ) -> ActionPlan:
        """
        Generate complete action plan with summary, checklist, and voice text.
        
        Args:
            reasoning_result: Clinical reasoning output
            language: Target language for output (normalized to lowercase)
        
        Returns:
            ActionPlan with all communication elements
        """
        # Normalize language to lowercase
        language = str(language).lower()
        
        primary_concern = reasoning_result.primary_concern
        triage_level = reasoning_result.triage_level
        
        # Generate summary text
        summary_text = self._generate_summary(
            primary_concern,
            reasoning_result,
            language
        )
        
        # Get action checklist
        action_checklist = self.ACTION_CHECKLISTS.get(
            triage_level.value,
            self.ACTION_CHECKLISTS["low"]
        ).get(language, self.ACTION_CHECKLISTS["low"]["english"])
        
        # Get emergency signs
        emergency_signs = self._get_emergency_signs(primary_concern, language)
        
        # Generate voice text (simplified summary)
        voice_text = self._generate_voice_text(
            primary_concern,
            triage_level,
            language
        )
        
        return ActionPlan(
            summary_text=summary_text,
            action_checklist=action_checklist,
            emergency_signs=emergency_signs,
            voice_text=voice_text,
            language=language
        )
    
    def _generate_summary(
        self,
        primary_concern: str,
        reasoning_result: ReasoningResult,
        language: str
    ) -> str:
        """Generate summary text with dynamic values"""
        
        template = self.SUMMARY_TEMPLATES.get(
            primary_concern,
            self.SUMMARY_TEMPLATES["general_health"]
        ).get(language, self.SUMMARY_TEMPLATES["general_health"]["english"])
        
        # Extract values for template
        bp = "N/A"
        glucose = "N/A"
        
        for fact in reasoning_result.reasoning_trace:
            if "BP" in fact.fact and "/" in fact.fact:
                bp = fact.fact.split("BP")[1].strip().split()[0]
            if "glucose" in fact.fact.lower():
                parts = fact.fact.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        glucose = part
                        break
        
        # Format template
        try:
            summary = template.format(bp=bp, glucose=glucose)
        except KeyError:
            summary = template
        
        return summary
    
    def _get_emergency_signs(self, primary_concern: str, language: str) -> List[str]:
        """Get emergency warning signs based on primary concern"""
        
        if "maternal" in primary_concern:
            key = "maternal"
        elif "anemia" in primary_concern:
            key = "anemia"
        else:
            key = "general"
        
        return self.EMERGENCY_SIGNS.get(key, self.EMERGENCY_SIGNS["general"]).get(
            language,
            self.EMERGENCY_SIGNS["general"]["english"]
        )
    
    def _generate_voice_text(
        self,
        primary_concern: str,
        triage_level: TriageLevel,
        language: str
    ) -> str:
        """Generate simplified voice text for TTS"""
        
        voice_templates = {
            "urgent": {
                "english": "Urgent medical attention required. Please visit health center immediately.",
                "hindi": "तत्काल चिकित्सा ध्यान आवश्यक। कृपया तुरंत स्वास्थ्य केंद्र जाएं।",
                "tamil": "அவசர மருத்துவ கவனம் தேவை. உடனடியாக சுகாதார மையத்திற்கு செல்லவும்.",
            },
            "high": {
                "english": "High risk detected. Visit health center within 24 hours.",
                "hindi": "उच्च जोखिम। 24 घंटे में स्वास्थ्य केंद्र जाएं।",
                "tamil": "அதிக ஆபத்து கண்டறியப்பட்டது. 24 மணி நேரத்தில் சுகாதார மையம் செல்லவும்.",
            },
            "moderate": {
                "english": "Moderate risk. Schedule health center visit within a few days.",
                "hindi": "मध्यम जोखिम। कुछ दिनों में स्वास्थ्य केंद्र जाएं।",
                "tamil": "மிதமான ஆபத்து. சில நாட்களில் சுகாதார மைய பார்வை திட்டமிடவும்.",
            },
            "low": {
                "english": "Low risk. Continue routine monitoring.",
                "hindi": "कम जोखिम। नियमित निगरानी जारी रखें।",
                "tamil": "குறைந்த ஆபத்து. வழக்கமான கண்காணிப்பு தொடரவும்.",
            }
        }
        
        return voice_templates.get(
            triage_level.value,
            voice_templates["low"]
        ).get(language, voice_templates["low"]["english"])
