# 🏥 TriageFlow - Reasoning-First Medical Triage System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg?style=flat&logo=React&logoColor=black)](https://reactjs.org/)
[![Gemini](https://img.shields.io/badge/Gemini-1.5_Flash-4285F4.svg?style=flat&logo=Google&logoColor=white)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=Docker&logoColor=white)](https://www.docker.com/)

**TriageFlow** is an AI-powered medical triage system designed for rural healthcare clinics. It uses **Gemini 1.5 Flash** with Chain-of-Thought (CoT) reasoning to provide transparent, defensible triage decisions.

## 🎯 Core Features

### **🧠 Reasoning Engine**
- **Chain-of-Thought Analysis**: Full transparency into AI decision-making
- **Uncertainty Quantification**: Confidence scoring (0.0-1.0)
- **Safety-First Fallback**: Defaults to Level 1 Emergency on system errors
- **5-Level Urgency Classification**: From life-threatening to non-urgent

### **🚑 MATS Integration**
- Mock Uthishta MATS (Multi-Agent Ambulance Tracking System) integration
- Automatic dispatch for Level 1 emergencies
- Logged dispatch events for audit trail

### **🎨 Testing Dashboard**
- Clean, minimalist React interface with Tailwind CSS
- Color-coded urgency badges (Red → Orange → Yellow → Blue → Green)
- Real-time reasoning trace display
- Flashing ambulance alert for critical cases

### **🐳 MLOps-Ready**
- Dockerized microservices architecture
- Health checks and restart policies
- Production-grade nginx configuration
- Easy deployment with docker-compose

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [API Documentation](#-api-documentation)
- [Development Setup](#-development-setup)
- [Docker Deployment](#-docker-deployment)
- [Configuration](#-configuration)
- [Safety & Ethics](#-safety--ethics)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (for containerized deployment)
- Gemini API Key ([Get one here](https://ai.google.dev/))

### Option 1: Docker Deployment (Recommended)

1. **Clone and configure**:
```bash
cd d:\Projects\CrtlAlt_Healthcare
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY
```

2. **Launch with Docker Compose**:
```bash
docker-compose up -d
```

3. **Access the application**:
- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add GEMINI_API_KEY
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TriageFlow System                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│  React Frontend  │ ◄─HTTP─►│  FastAPI Backend │
│  (Tailwind CSS)  │         │   (Port 8000)    │
└──────────────────┘         └────────┬─────────┘
                                      │
                                      ├─► Gemini 1.5 Flash API
                                      │   (Chain-of-Thought)
                                      │
                                      └─► MATS Dispatch Service
                                          (Mock Integration)
```

### **Data Flow**
1. User inputs symptoms via React dashboard
2. Frontend sends POST request to `/triage` endpoint
3. Backend constructs CoT prompt for Gemini
4. Gemini performs reasoning and returns structured JSON
5. Backend parses response, applies safety checks
6. If Level 1 urgency, triggers MATS ambulance dispatch
7. Frontend displays results with color-coded urgency + reasoning trace

---

## 📡 API Documentation

### **POST /triage**

Perform AI-powered triage analysis.

**Request Body:**
```json
{
  "text_description": "Patient reports severe chest pain radiating to left arm, difficulty breathing, sweating",
  "image_url": "https://example.com/image.jpg" // Optional
}
```

**Response:**
```json
{
  "urgency_level": 1,
  "clinical_reasoning": "**CHAIN-OF-THOUGHT ANALYSIS:**\n\n1. Identified red flags: chest pain, arm radiation, dyspnea\n2. Assessed cardiovascular emergency indicators...",
  "uncertainty_score": 0.15,
  "safety_flag": true,
  "dispatch_ambulance": true,
  "timestamp": "2026-02-06T14:30:00Z"
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `urgency_level` | int (1-5) | 1=Life-threatening, 5=Non-urgent |
| `clinical_reasoning` | string | Full CoT reasoning trace |
| `uncertainty_score` | float (0.0-1.0) | Model uncertainty (higher = less confident) |
| `safety_flag` | boolean | True if high uncertainty or critical symptoms |
| `dispatch_ambulance` | boolean | True only for Level 1 emergencies |
| `timestamp` | string (ISO 8601) | UTC timestamp of analysis |

**Error Handling:**
- **400 Bad Request**: Invalid input (missing/too short description)
- **500 Internal Server Error**: Gemini API failure → Defaults to Level 1 with safety fallback
- **503 Service Unavailable**: Backend not configured properly

### **GET /**

Health check endpoint.

**Response:**
```json
{
  "status": "operational",
  "service": "TriageFlow API",
  "version": "1.0.0",
  "gemini_configured": true
}
```

---

## 🛠️ Development Setup

### Backend Development

**File Structure:**
```
backend/
├── app/
│   └── main.py          # FastAPI application + Gemini integration
├── Dockerfile           # Production container config
├── requirements.txt     # Python dependencies
└── .env.example         # Environment template
```

**Adding New Features:**
1. Modify `app/main.py` for new endpoints
2. Update `TriageResponse` model for additional fields
3. Test with `pytest` (add tests in `tests/` directory)
4. Update API documentation in this README

### Frontend Development

**File Structure:**
```
frontend/
├── src/
│   ├── App.jsx          # Main React component
│   ├── main.jsx         # Entry point
│   └── index.css        # Tailwind styles
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind customization
└── package.json         # Node dependencies
```

**Customizing UI:**
- Urgency colors: Edit `URGENCY_CONFIG` in `App.jsx`
- Tailwind theme: Modify `tailwind.config.js`
- Add new components in `src/components/`

---

## 🐳 Docker Deployment

### Production Deployment

**1. Build Images:**
```bash
docker-compose build
```

**2. Run in Production:**
```bash
docker-compose up -d
```

**3. View Logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**4. Stop Services:**
```bash
docker-compose down
```

### Health Checks

Both services include health checks:
- **Backend**: HTTP GET to `http://localhost:8000/`
- **Frontend**: nginx server check

Monitor health:
```bash
docker ps  # Check STATUS column for (healthy)
```

### Scaling (Future)

For production load:
```bash
docker-compose up -d --scale backend=3
# Add nginx load balancer in front
```

---

## ⚙️ Configuration

### Environment Variables

**Backend (.env):**
```bash
# Required
GEMINI_API_KEY=your_actual_api_key_here

# Optional - MATS Integration
MATS_API_ENDPOINT=https://api.mats.uthishta.com/dispatch
MATS_API_KEY=your_mats_key

# Server Config
HOST=0.0.0.0
PORT=8000
```

### Gemini Model Configuration

To switch models, edit `backend/app/main.py`:
```python
model = genai.GenerativeModel('gemini-1.5-pro')  # More powerful, slower
# or
model = genai.GenerativeModel('gemini-1.5-flash')  # Faster, cost-effective
```

### Triage Prompt Tuning

Modify `TRIAGE_SYSTEM_PROMPT` in `main.py` to:
- Adjust reasoning steps
- Change urgency criteria
- Add domain-specific knowledge

---

## 🛡️ Safety & Ethics

### Safety Mechanisms

1. **Chain-of-Thought Transparency**: All reasoning steps are logged and displayed
2. **Uncertainty Quantification**: System flags low-confidence predictions
3. **Safety Fallback**: On error, defaults to Level 1 (Emergency) + manual review
4. **Human-in-the-Loop**: Safety flags trigger mandatory clinician review
5. **Audit Trail**: All triage decisions logged with timestamps

### Ethical Considerations

⚠️ **IMPORTANT**: This is a **decision-support tool**, NOT a replacement for medical professionals.

- **Regulatory Status**: Prototype for hackathon/research use only
- **Clinical Validation**: Requires extensive validation before real-world deployment
- **Liability**: Healthcare providers remain responsible for final decisions
- **Bias Mitigation**: Continuously monitor for demographic biases in triage outcomes
- **Data Privacy**: Implement HIPAA/GDPR compliance before handling real patient data

### Limitations

- **No Image Analysis**: Current version uses text-only (image_url accepted but not processed)
- **Limited Medical Knowledge**: Based on Gemini's training cutoff
- **No Electronic Health Record Integration**: Standalone system
- **Mock MATS Integration**: Ambulance dispatch is simulated

---

## 🧪 Testing

### Manual Testing Cases

**Test Case 1: Life-Threatening Emergency**
```
Input: "Patient unconscious, no pulse, not breathing"
Expected: Level 1, dispatch_ambulance=true, safety_flag=true
```

**Test Case 2: High Uncertainty**
```
Input: "Feeling unwell"
Expected: High uncertainty_score (>0.7), safety_flag=true
```

**Test Case 3: Non-Urgent**
```
Input: "Mild headache for 1 day, no other symptoms"
Expected: Level 4 or 5, dispatch_ambulance=false
```

### Automated Testing (Future)

```bash
cd backend
pytest tests/
```

---

## 📊 Monitoring & Logging

### Backend Logs

Key events logged:
- Triage request received
- Gemini API calls
- MATS dispatch triggers (CRITICAL level)
- Error fallbacks

**View real-time logs:**
```bash
docker-compose logs -f backend
```

### Metrics to Track (Production)

- Average urgency level distribution
- Uncertainty score statistics
- API response times
- Gemini API error rate
- Ambulance dispatch frequency

---

## 🤝 Contributing

This is a hackathon project. For improvements:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is for educational and research purposes. Contact authors for commercial use.

---

## 👨‍💻 Developer Info

**Built by**: AI Engineering Student  
**Stack**: FastAPI + React + Gemini 1.5 Flash + Docker  
**Status**: Hackathon Prototype (v1.0.0)  
**MLOps Ready**: Yes - Dockerized, health-checked, scalable architecture

---

## 🔗 Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 🚀 Roadmap

- [ ] Real image analysis integration (vision models)
- [ ] Multi-language support
- [ ] EHR system integration (FHIR standard)
- [ ] Real-time MATS API connection
- [ ] Mobile app (React Native)
- [ ] Offline mode for rural connectivity issues
- [ ] Clinical validation study
- [ ] Regulatory compliance (FDA, CE marking)

---

**Need Help?** Check logs with `docker-compose logs -f` or file an issue.

**Ready to Deploy?** Run `docker-compose up -d` and access http://localhost:3000 🎉
