
import { GoogleGenAI, Type } from "@google/genai";
import { PatientInput, TriageResponse } from "../types";

// Initialize Gemini
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const RESPONSE_SCHEMA = {
  type: Type.OBJECT,
  properties: {
    upload_status: { type: Type.STRING },
    progress_tracker: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          stage: { type: Type.STRING },
          status: { type: Type.STRING },
        },
      },
    },
    risk_classification: { type: Type.STRING },
    condition_summary: { type: Type.STRING },
    triage_category: { type: Type.STRING, enum: ["Low", "Moderate", "High", "Emergency"] },
    recommended_actions: {
      type: Type.ARRAY,
      items: { type: Type.STRING },
    },
    nutrition_and_lifestyle_advice: {
      type: Type.ARRAY,
      items: { type: Type.STRING },
    },
    followup_and_referral_guidance: { type: Type.STRING },
    notification_message_for_patient: { type: Type.STRING },
    doctor_or_phc_message: { type: Type.STRING },
    ui_improvement_suggestions: {
      type: Type.ARRAY,
      items: { type: Type.STRING },
    },
  },
  required: [
    "risk_classification",
    "condition_summary",
    "triage_category",
    "recommended_actions",
    "notification_message_for_patient",
  ],
};

export const analyzePatientCase = async (data: PatientInput): Promise<TriageResponse> => {
  const modelId = "gemini-2.5-flash";

  const systemInstruction = `
    You are an expert Multi-Agent Clinical Reasoning AI assisting frontline healthcare workers (ASHA) in rural India.
    Your goal is to interpret vitals, symptoms, and images to produce a structured, medically reasoned triage result.
    
    Context:
    - User is an ASHA worker (non-doctor).
    - Output must be simple, clear, and supportive.
    - Avoid complex jargon; explain medical terms if used.
    - Prioritize identifying emergencies (Red flags).
    
    === LANGUAGE REQUIREMENT ===
    The user has selected the language: "${data.language || 'English'}".
    **CRITICAL**: All natural language output fields (condition_summary, recommended_actions, nutrition_and_lifestyle_advice, notification_message_for_patient) MUST be written in ${data.language || 'English'}.
    If the language is Tamil, Telugu, or Hindi, use the native script (not transliteration).
    Examples:
    - Tamil: "உங்கள் இரத்த அழுத்தம் அதிகமாக ఉంది..." (Use proper Tamil script)
    - Hindi: "आपका रक्तचाप उच्च है..."

    === NOTIFICATION TEMPLATES (STRICT) ===
    For 'notification_message_for_patient', follow this format EXACTLY (translated to target language):
    "Your AI screening report is ready. Risk level: [Triage Category]. Click link to view & download PDF. Please consult PHC if symptoms worsen."

    === SPECIALIZED CLINICAL PROTOCOLS ===

    1. GESTATIONAL DIABETES MELLITUS (GDM) SCREENING
       **Trigger:** Patient is Pregnant (pregnant == true).
       **Analysis Logic:**
       - **Vitals:** Check Random Glucose (random_glucose).
         - *< 140 mg/dL:* Low immediate risk (unless symptoms present).
         - *140 - 199 mg/dL:* Suspected GDM. Risk Level: MODERATE or HIGH depending on symptoms. Action: Refer for confirmed OGTT.
         - *>= 200 mg/dL:* High suspicion of Overt Diabetes/GDM. Risk Level: HIGH or EMERGENCY.
       - **Risk Factors:** Age > 30, High BMI (inferred if swelling/edema present), Family history.
       - **Symptoms:** Frequent urination (polyuria), Excessive thirst (polydipsia), Blurred vision, Fatigue.
       - **Output Requirement:**
         - In 'condition_summary', specifically mention "Screening for Gestational Diabetes: [Result]".
         - If Glucose is high, provide specific nutrition advice (small frequent meals, low glycemic index, avoid sugar) in 'nutrition_and_lifestyle_advice'.

    2. PRE-ECLAMPSIA SCREENING (Pregnant Patients)
       - **Trigger:** Patient is Pregnant.
       - **Analysis:** If BP Systolic >= 140 OR Diastolic >= 90.
       - **Symptoms:** Headache, Blurred Vision, Swelling (Face/Hands).
       - **Result:** HIGH or EMERGENCY risk. Immediate referral required.

    3. GENERAL TRIAGE (Non-Pregnant)
       - Hypertension: > 140/90.
       - Diabetes: Random Glucose > 200 mg/dL.
       - Infection: Fever + High Heart Rate.
       - Anemia: Low SpO2, Pale conjunctiva (if image provided).
    
    Tasks:
    1. Analyze the provided JSON data and any images.
    2. Determine risk level (Low/Moderate/High/Emergency).
    3. Provide actionable advice (Lifestyle/Nutrition/Referral).
    4. Adhere strictly to the JSON output format.
  `;

  // Prepare prompt parts
  const parts: any[] = [];

  // 1. Add the data as a JSON string
  parts.push({
    text: `Analyze this patient data:\n${JSON.stringify(data, null, 2)}`,
  });

  // 2. Add images if present
  if (data.images.conjunctiva) {
    parts.push({
      inlineData: {
        mimeType: "image/jpeg",
        data: data.images.conjunctiva,
      },
    });
    parts.push({ text: "[Image attached: Conjunctiva photo for anemia check]" });
  }

  if (data.images.swelling) {
    parts.push({
      inlineData: {
        mimeType: "image/jpeg",
        data: data.images.swelling,
      },
    });
    parts.push({ text: "[Image attached: Swelling/Edema check]" });
  }

  if (data.images.skin) {
    parts.push({
      inlineData: {
        mimeType: "image/jpeg",
        data: data.images.skin,
      },
    });
    parts.push({ text: "[Image attached: Skin condition]" });
  }

  try {
    const response = await ai.models.generateContent({
      model: modelId,
      contents: {
        parts: parts,
      },
      config: {
        systemInstruction: systemInstruction,
        responseMimeType: "application/json",
        responseSchema: RESPONSE_SCHEMA,
      },
    });

    if (response.text) {
      return JSON.parse(response.text) as TriageResponse;
    } else {
      throw new Error("Empty response from AI");
    }
  } catch (error) {
    console.error("AI Analysis Failed:", error);
    throw error;
  }
};
