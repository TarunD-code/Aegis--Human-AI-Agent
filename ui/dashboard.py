"""
Aegis v3.6 — Remote UI Dashboard 
================================
Opt-in minimal FastAPI application to view AI logs and approve plans asynchronously.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Aegis Remote Dashboard")

@app.get("/logs/ai_plan")
def get_recent_plans():
    return JSONResponse({"status": "not_implemented", "msg": "Dashboard is in preview"})

@app.post("/plans/{plan_id}/approve")
def approve_plan(plan_id: str):
    return {"status": "success", "plan_id": plan_id}
