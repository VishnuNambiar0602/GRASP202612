import sys
import os
from unittest.mock import MagicMock

# Add backend directory to sys.path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock google.generativeai before importing main
mock_genai = MagicMock()
sys.modules["google.generativeai"] = mock_genai

from fastapi.testclient import TestClient
from app.main import app, analyze_triage_with_gemini

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

def test_triage_validation_error():
    response = client.post("/triage", json={"text_description": "bad"})
    # The validation logic in perform_triage: len(request.text_description.strip()) < 5
    assert response.status_code == 400
    assert "Symptom description too short" in response.json()["detail"]

def test_triage_gemini_mock_success():
    # Setup mock response
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model

    mock_response = MagicMock()
    # Mock a valid JSON response from Gemini
    mock_response.text = """
    ```json
    {
        "reasoning_steps": ["Step 1: Test", "Step 2: Analysis"],
        "urgency_level": 3,
        "uncertainty_score": 0.2,
        "red_flags": [],
        "recommended_action": "Monitor"
    }
    ```
    """
    mock_model.generate_content.return_value = mock_response

    response = client.post("/triage", json={"text_description": "Patient has a headache for 2 days."})

    assert response.status_code == 200
    data = response.json()
    assert data["urgency_level"] == 3
    assert data["dispatch_ambulance"] is False
    assert "Step 1: Test" in data["clinical_reasoning"]

    # Verify the correct model was initialized
    mock_genai.GenerativeModel.assert_called_with('gemini-1.5-flash')

def test_triage_gemini_fallback():
    # Setup mock to raise exception
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    mock_model.generate_content.side_effect = Exception("API Error")

    response = client.post("/triage", json={"text_description": "Serious condition"})

    assert response.status_code == 200 # It should return 200 with fallback data
    data = response.json()
    assert data["urgency_level"] == 1
    assert data["safety_flag"] is True
    assert data["dispatch_ambulance"] is True
    assert "SAFETY FALLBACK ACTIVATED" in data["clinical_reasoning"]

def test_json_regex_flexibility():
    # Test different JSON formats response from Gemini

    # 1. No language tag
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    mock_response = MagicMock()
    mock_response.text = """
    ```
    {
        "reasoning_steps": ["Step 1"],
        "urgency_level": 5,
        "uncertainty_score": 0.1,
        "red_flags": [],
        "recommended_action": "Rest"
    }
    ```
    """
    mock_model.generate_content.return_value = mock_response

    # We call analyze_triage_with_gemini directly to avoid client overhead for this unit test
    result = analyze_triage_with_gemini("symptoms")
    assert result.urgency_level == 5

    # 2. JSON caps
    mock_response.text = """
    ```JSON
    {
        "reasoning_steps": ["Step 1"],
        "urgency_level": 4,
        "uncertainty_score": 0.1,
        "red_flags": [],
        "recommended_action": "Rest"
    }
    ```
    """
    result = analyze_triage_with_gemini("symptoms")
    assert result.urgency_level == 4

    # 3. No code blocks (just JSON) - This might fail if the code strictly expects code blocks?
    # backend code says:
    # json_match = re.search(...)
    # if json_match: ...
    # else: parsed = json.loads(response_text)

    mock_response.text = """
    {
        "reasoning_steps": ["Step 1"],
        "urgency_level": 2,
        "uncertainty_score": 0.1,
        "red_flags": [],
        "recommended_action": "Rest"
    }
    """
    result = analyze_triage_with_gemini("symptoms")
    assert result.urgency_level == 2
