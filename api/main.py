"""
api/main.py - FastAPI Backend for Automaton Auditor Swarm
Production Module v1.0.0
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your LangGraph auditor
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.graph import run_full_audit

app = FastAPI(
    title="Automaton Auditor Swarm API",
    description="Production API for autonomous code auditing",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# REQUEST/RESPONSE SCHEMAS
# =============================================================================

class AuditRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL to audit")
    pdf_path: Optional[str] = Field(None, description="Path to architectural report PDF")
    mode: str = Field(default="full", description="Audit mode: detective or full")

class AuditResponse(BaseModel):
    audit_id: str
    status: str
    message: str
    result_url: Optional[str] = None

class AuditResult(BaseModel):
    audit_id: str
    status: str
    final_report: Optional[Dict[str, Any]] = None
    report_markdown: Optional[str] = None
    error: Optional[str] = None

# =============================================================================
# IN-MEMORY STORE (Replace with Redis/Postgres for production)
# =============================================================================

audit_store: Dict[str, Dict[str, Any]] = {}

# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint for Docker/K8s"""
    return {"status": "healthy", "service": "automaton-auditor-api"}

@app.post("/api/audit", response_model=AuditResponse)
async def submit_audit(request: AuditRequest, background_tasks: BackgroundTasks):
    """
    Submit a new audit request.
    Returns immediately with audit_id; results available via /api/audit/{id}
    """
    audit_id = str(uuid.uuid4())
    
    # Store initial state
    audit_store[audit_id] = {
        "status": "processing",
        "request": request.model_dump(),
        "result": None,
        "error": None
    }
    
    # Run audit in background
    background_tasks.add_task(run_audit_async, audit_id, request)
    
    return AuditResponse(
        audit_id=audit_id,
        status="processing",
        message="Audit submitted successfully. Check status via /api/audit/{id}",
        result_url=f"/api/audit/{audit_id}"
    )

@app.get("/api/audit/{audit_id}", response_model=AuditResult)
async def get_audit_result(audit_id: str):
    """
    Get audit status or results.
    """
    if audit_id not in audit_store:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    audit = audit_store[audit_id]
    
    if audit["status"] == "processing":
        return AuditResult(
            audit_id=audit_id,
            status="processing",
            message="Audit in progress..."
        )
    elif audit["status"] == "failed":
        return AuditResult(
            audit_id=audit_id,
            status="failed",
            error=audit["error"]
        )
    else:
        # Return completed results
        result = audit["result"]
        return AuditResult(
            audit_id=audit_id,
            status="completed",
            final_report=result.get("final_report"),
            report_markdown=result.get("report_markdown"),
            error=None
        )

# =============================================================================
# BACKGROUND TASK: RUN AUDIT
# =============================================================================

async def run_audit_async(audit_id: str, request: AuditRequest):
    """
    Execute the audit in background and store results.
    
    Note: run_full_audit() already returns report_markdown, so no additional
    serialization is needed here.
    """
    try:
        # Run your existing auditor
        # run_full_audit already returns report_markdown in the result dict
        result = run_full_audit(
            repo_url=request.repo_url,
            pdf_path=request.pdf_path,
            rubric_dimensions=None,
            mode=request.mode,
            output_path=None  # Don't save to file via CLI path
        )
        
        # Store completed result
        # result already contains: final_report, report_markdown, etc.
        audit_store[audit_id].update({
            "status": "completed",
            "result": result
        })
        
        print(f"Audit {audit_id} completed successfully")
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        audit_store[audit_id].update({
            "status": "failed",
            "error": error_msg
        })
        print(f"Audit {audit_id} failed: {error_msg}")
        import traceback
        traceback.print_exc()

# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8001,  # Match your frontend config
        reload=os.getenv("ENV") == "development"
    )