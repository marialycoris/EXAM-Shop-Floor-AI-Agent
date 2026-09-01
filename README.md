# EXAM-Shop-Floor-AI-Agent

This repository now contains two applications:

- `frontend`: React + TypeScript + Tailwind CSS (Vite)
- `backend`: Python + Flask

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Build:

```bash
npm run build
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Health endpoint:

- `GET /api/health`
