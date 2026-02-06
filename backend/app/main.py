"""
TriageFlow - FastAPI Backend
Reasoning-First Triage System with Gemini 1.5 Flash Integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List
import google.generativeai as genai
import os
import logging
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TriageFlow API",
    description="Reasoning-First Medical Triage System",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set - API will use fallback safety mode")


# Request/Response Models
class TriageRequest(BaseModel):
    text_description: str = Field(..., description="Patient symptom description")
    image_url: Optional[str] = Field(None, description="Optional image URL for visual triage")


class GeminiTriageOutput(BaseModel):
    """Pydantic model for Gemini's expected JSON output"""
    reasoning_steps: List[str] = Field(..., description="Step-by-step reasoning")
    urgency_level: int = Field(..., ge=1, le=5, description="1=Life-threatening, 5=Non-urgent")
    uncertainty_score: float = Field(..., ge=0.0, le=1.0, description="Model uncertainty")
    red_flags: List[str] = Field(default_factory=list, description="Concerning symptoms")
    recommended_action: str = Field(..., description="Brief action summary")


class TriageResponse(BaseModel):
    urgency_level: int = Field(..., ge=1, le=5, description="1=Life-threatening, 5=Non-urgent")
    clinical_reasoning: str = Field(..., description="Detailed CoT reasoning trace")
    uncertainty_score: float = Field(..., ge=0.0, le=1.0, description="Model confidence uncertainty")
    safety_flag: bool = Field(..., description="True if high uncertainty or ambiguous symptoms")
    dispatch_ambulance: bool = Field(..., description="True if immediate ambulance needed")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# Chain-of-Thought System Prompt for Gemini
TRIAGE_SYSTEM_PROMPT = """You are an expert medical triage AI assistant for a rural healthcare clinic. Your role is to perform systematic triage assessment using Chain-of-Thought (CoT) reasoning.

**CRITICAL INSTRUCTIONS:**
1. You MUST provide detailed step-by-step reasoning before assigning an urgency level.
2. If symptoms are ambiguous or insufficient, you MUST flag high uncertainty.
3. Always err on the side of caution for patient safety.

**URGENCY LEVELS:**
- Level 1: Life-threatening (cardiac arrest, severe trauma, stroke symptoms, difficulty breathing, severe bleeding)
- Level 2: Emergency (chest pain, severe pain, high fever with altered mental status)
- Level 3: Urgent (moderate pain, fever, vomiting, minor injuries)
- Level 4: Semi-urgent (mild symptoms, chronic conditions)
- Level 5: Non-urgent (routine care, minor ailments)

**RESPONSE FORMAT (JSON):**
{{
  "reasoning_steps": [
    "Step 1: Identify key symptoms...",
    "Step 2: Assess severity indicators...",
    "Step 3: Consider differential diagnoses...",
    "Step 4: Evaluate time sensitivity..."
  ],
  "urgency_level": <1-5>,
  "uncertainty_score": <0.0-1.0>,
  "red_flags": ["list any concerning symptoms"],
  "recommended_action": "brief action summary"
}}

**INPUT:** Patient describes: {symptoms}

**YOUR ANALYSIS:**"""


def extract_numbered_steps_from_text(text: str) -> List[str]:
    """
    Fallback: Extract numbered list from text using regex if JSON parsing fails.
    Matches patterns like:
    - 1. Step one
    - Step 1: Something
    - 1) Step one
    """
    patterns = [
        r'(?:^|\n)\s*(\d+)\.\s+(.+?)(?=\n\s*\d+\.|$)',  # 1. Step
        r'(?:^|\n)\s*Step\s+(\d+):\s+(.+?)(?=\n\s*Step\s+\d+:|$)',  # Step 1:
        r'(?:^|\n)\s*(\d+)\)\s+(.+?)(?=\n\s*\d+\)|$)',  # 1) Step
    ]
    
    steps = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
        if matches:
            steps = [match[1].strip() if isinstance(match, tuple) else match.strip() 
                    for match in matches]
            break
    
    return steps if steps else ["Unable to extract structured reasoning from response"]


def parse_gemini_response(response_text: str) -> GeminiTriageOutput:
    """
    Parse Gemini's JSON response using Pydantic validation.
    Falls back to regex extraction if reasoning_steps is missing.
    """
    import json
    
    logger.info(f"Raw Gemini response (first 500 chars): {response_text[:500]}")
    
    try:
        # Try to extract JSON from code blocks if present
        json_match = re.search(r'```(?:[a-zA-Z]+)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
            logger.info("Extracted JSON from code block")
        
        # Parse JSON
        parsed = json.loads(response_text)
        logger.info(f"Successfully parsed JSON with keys: {list(parsed.keys())}")
        
        # If reasoning_steps is missing, try to extract from text
        if 'reasoning_steps' not in parsed or not parsed['reasoning_steps']:
            logger.warning("reasoning_steps missing, attempting regex extraction from original response")
            # Use original response_text before JSON extraction
            extracted_steps = extract_numbered_steps_from_text(response_text)
            parsed['reasoning_steps'] = extracted_steps
            logger.info(f"Extracted {len(extracted_steps)} steps via regex")
        
        # Validate with Pydantic model
        gemini_output = GeminiTriageOutput(**parsed)
        logger.info("Successfully validated with Pydantic model")
        return gemini_output
        
    except (json.JSONDecodeError, ValidationError, KeyError) as e:
        logger.error(f"Parse/validation error type: {type(e).__name__}")
        logger.error(f"Parse/validation error: {str(e)}")
        logger.error(f"Full raw response: {response_text}")
        raise


def trigger_mats_dispatch(patient_data: dict) -> None:
    """
    Mock function for Uthishta MATS Ambulance Tracking System integration.
    In production, this would connect to the actual MATS API.
    """
    logger.critical("=" * 80)
    logger.critical("🚨 INTEGRATION: Triggering Uthishta MATS Ambulance Tracking Protocol 🚨")
    logger.critical(f"Patient Urgency: Level {patient_data.get('urgency_level')}")
    logger.critical(f"Timestamp: {patient_data.get('timestamp')}")
    logger.critical(f"Clinical Reasoning: {patient_data.get('clinical_reasoning')[:100]}...")
    logger.critical("=" * 80)
    
    # TODO: Implement actual MATS API integration
    # requests.post(MATS_API_ENDPOINT, json=patient_data)


def analyze_triage_with_gemini(symptoms: str, image_url: Optional[str] = None) -> TriageResponse:
    """
    Core reasoning engine using Gemini 2.5 Flash with Chain-of-Thought.
    Includes robust error handling with retry logic and safety fallback.
    
    Retry Strategy:
    1. First attempt: Standard prompt
    2. If JSON malformed: Ask Gemini to reformat as strict JSON
    3. If still fails: Activate safety fallback (Level 1 + manual review)
    """
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare prompt
        prompt = TRIAGE_SYSTEM_PROMPT.format(symptoms=symptoms)
        
        # Generate response (First attempt)
        logger.info(f"Analyzing symptoms: {symptoms[:100]}...")
        response = model.generate_content(prompt)
        logger.info(f"Gemini response type: {type(response)}")
        logger.info(f"Gemini response attributes: {dir(response)}")
        logger.info(f"Gemini response.text type: {type(response.text)}")
        logger.info(f"Gemini response.text (first 500 chars): {str(response.text)[:500]}")
        
        try:
            # Parse response with Pydantic validation
            gemini_output = parse_gemini_response(response.text)
            logger.info("First parse attempt succeeded")
            
        except Exception as parse_error:
            # RETRY LOGIC: Ask Gemini to reformat as strict JSON
            logger.warning(f"Initial parse failed ({type(parse_error).__name__}: {parse_error})")
            logger.warning("Attempting retry with reformatting request...")
            
            retry_prompt = f"""The previous response was not in valid JSON format. 
Please reformat the exact same medical analysis as strict JSON following this schema:

{{
  "reasoning_steps": ["Step 1: ...", "Step 2: ...", "Step 3: ...", "Step 4: ..."],
  "urgency_level": <1-5>,
  "uncertainty_score": <0.0-1.0>,
  "red_flags": ["flag1", "flag2"],
  "recommended_action": "brief action"
}}

Previous response to reformat:
{response.text}
"""
            
            retry_response = model.generate_content(retry_prompt)
            
            try:
                # Second parse attempt
                gemini_output = parse_gemini_response(retry_response.text)
                logger.info("Retry successful - JSON reformatted correctly")
                
            except Exception as retry_parse_error:
                # Both attempts failed - trigger safety fallback
                logger.error(f"Retry parse also failed: {retry_parse_error}")
                raise Exception("JSON parsing failed after retry")
        
        # Extract validated data from Pydantic model
        urgency_level = gemini_output.urgency_level
        uncertainty_score = gemini_output.uncertainty_score
        reasoning_steps = gemini_output.reasoning_steps
        red_flags = gemini_output.red_flags
        recommended_action = gemini_output.recommended_action
        
        # Construct clinical reasoning trace
        clinical_reasoning = "**CHAIN-OF-THOUGHT ANALYSIS:**\n\n"
        for i, step in enumerate(reasoning_steps, 1):
            clinical_reasoning += f"{i}. {step}\n"
        
        clinical_reasoning += f"\n**RED FLAGS IDENTIFIED:** {', '.join(red_flags) if red_flags else 'None'}\n"
        clinical_reasoning += f"\n**RECOMMENDED ACTION:** {recommended_action}\n"
        
        # Determine safety flag (high uncertainty or critical symptoms)
        safety_flag = (uncertainty_score > 0.7) or (urgency_level <= 2) or bool(red_flags)
        
        # Determine ambulance dispatch (only for Level 1)
        dispatch_ambulance = (urgency_level == 1)
        
        return TriageResponse(
            urgency_level=urgency_level,
            clinical_reasoning=clinical_reasoning,
            uncertainty_score=uncertainty_score,
            safety_flag=safety_flag,
            dispatch_ambulance=dispatch_ambulance
        )
        
    except Exception as e:
        # SAFETY FALLBACK: Default to emergency with manual review
        logger.error(f"Gemini API Error: {str(e)}")
        logger.critical("SAFETY FALLBACK ACTIVATED - Defaulting to Level 1 Emergency")
        
        return TriageResponse(
            urgency_level=1,
            clinical_reasoning=(
                f"**SYSTEM ERROR - SAFETY FALLBACK ACTIVATED**\n\n"
                f"The AI triage system encountered an error: {str(e)}\n\n"
                f"**SAFETY PROTOCOL:** Due to system limitations, this case has been "
                f"automatically escalated to Level 1 (Emergency) and requires immediate "
                f"manual review by qualified medical personnel.\n\n"
                f"**Original Symptoms:** {symptoms}\n\n"
                f"**Action Required:** Human clinician assessment MANDATORY."
            ),
            uncertainty_score=1.0,
            safety_flag=True,
            dispatch_ambulance=True  # Safety-first approach
        )


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "operational",
        "service": "TriageFlow API",
        "version": "1.0.0",
        "gemini_configured": bool(GEMINI_API_KEY)
    }


@app.post("/triage", response_model=TriageResponse)
async def perform_triage(request: TriageRequest):
    """
    Main triage endpoint with Gemini-powered reasoning engine.
    
    **Safety Features:**
    - Chain-of-Thought reasoning for transparency
    - Uncertainty quantification
    - Automatic fallback to emergency for system errors
    - MATS ambulance dispatch for Level 1 urgencies
    """
    try:
        logger.info(f"Received triage request: {len(request.text_description)} chars")
        
        # Validate input
        if not request.text_description or len(request.text_description.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="Symptom description too short. Please provide detailed symptoms."
            )
        
        # Perform AI-powered triage analysis
        result = analyze_triage_with_gemini(
            symptoms=request.text_description,
            image_url=request.image_url
        )
        
        # Trigger ambulance dispatch if needed
        if result.dispatch_ambulance:
            trigger_mats_dispatch({
                "urgency_level": result.urgency_level,
                "clinical_reasoning": result.clinical_reasoning,
                "timestamp": result.timestamp,
                "symptoms": request.text_description
            })
        
        logger.info(f"Triage completed: Level {result.urgency_level}, Uncertainty: {result.uncertainty_score:.2f}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in triage endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
