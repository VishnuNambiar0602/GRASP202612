# TriageFlow - Quick Start Guide

## 🚀 Fast Setup (5 Minutes)

### Step 1: Get Gemini API Key
1. Visit: https://ai.google.dev/
2. Click "Get API Key" → Create new API key
3. Copy your key

### Step 2: Configure Backend
```bash
cd backend
copy .env.example .env
# Open .env in notepad and paste your API key:
# GEMINI_API_KEY=paste_your_key_here
```

### Step 3: Run with Docker
```bash
cd ..
docker-compose up -d
```

### Step 4: Open Dashboard
- Browser: http://localhost:3000
- Test with: "Patient has severe chest pain and difficulty breathing"

## 🛠️ Local Development (No Docker)

### Backend:
```bash
cd backend
pip install -r requirements.txt
# Configure .env first!
uvicorn app.main:app --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📝 Test Symptoms

**Emergency (Level 1):**
- "Patient unconscious, no pulse"
- "Severe chest pain radiating to jaw, difficulty breathing"
- "Uncontrolled bleeding from head injury"

**Urgent (Level 3):**
- "High fever 103°F for 2 days, severe headache"
- "Persistent vomiting for 8 hours"

**Non-Urgent (Level 5):**
- "Mild sore throat for 1 day"
- "Minor cut on finger, bleeding controlled"

## ❗ Troubleshooting

**"Failed to connect to API":**
- Check backend is running: http://localhost:8000
- Verify GEMINI_API_KEY is set in backend/.env

**"Error 500 - Safety Fallback":**
- Check backend logs: `docker-compose logs backend`
- Ensure API key is valid and has quota

**Frontend won't start:**
- Delete node_modules and run `npm install` again
- Check Node.js version: `node --version` (need 20+)

## 🎓 Learning Resources

- **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **React Basics**: https://react.dev/learn
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Gemini API Docs**: https://ai.google.dev/docs

---

**Ready?** Run `docker-compose up -d` and visit http://localhost:3000 🎉
