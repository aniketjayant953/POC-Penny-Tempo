# Tempo POC

AI coaching intelligence demo: React/TypeScript frontend + FastAPI backend wrapping the existing Python logic in `src/`.

## Run

Backend (project root, Python env with `pip install -r requirements.txt`; LLM settings come from `src/.env`):

```
uvicorn backend.main:app --reload
```

Frontend (Node 20+):

```
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (API on http://localhost:8000, docs at /docs).
Optional: set `VITE_API_URL` to point the frontend at a different API URL.

Coach data comes from `data/Candidate-coach sample data_v2.0.xlsx`.

## Structure

- `src/` existing business logic (unchanged)
- `backend/main.py` thin REST layer; all data access via `src/data_loader.load_data()`
- `frontend/` Vite + React + Tailwind + FullCalendar + Recharts
- `data/Candidate-coach sample data_v2.0.xlsx` source workbook for coaches, meetings, notes, and activities
