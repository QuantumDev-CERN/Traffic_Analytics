# HackZilla Traffic AI

AI-powered Delhi-NCR congestion predictor built from `HACKZILLA_MASTER.md`.

## Run Backend

Use Python 3.11 for the full pinned ML stack:

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
PYTHONPATH=backend .venv/bin/uvicorn api.main:app --reload --port 8000
```

This workstation is on Python 3.14, so the verified local fallback used current compatible packages for the API/runtime.

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Verified

```bash
PYTHONPATH=backend .venv/bin/python -m pytest tests -q
cd frontend && npm run build
cd frontend && npm run test:responsive
```

`npm run test:responsive` expects the backend at `http://localhost:8000` and frontend at `http://localhost:5173`.
