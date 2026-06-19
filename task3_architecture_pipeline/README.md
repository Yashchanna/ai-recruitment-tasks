Task 3: Architecture Pipeline

API endpoints:
- GET /api/generate?q=hello  (placeholder)
- POST /api/generate  with JSON {"requirements": "..."} returns a small architecture plan

Run locally:
python -m uvicorn task3_architecture_pipeline.api.generate:app --reload --port 8000

Vercel: use the included vercel.json to deploy the api/ folder as serverless functions.
