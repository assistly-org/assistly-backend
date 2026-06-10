from fastapi import APIRouter, Request
from fastapi import FastAPI, Depends # <-- Import Depends
from app.infrastructure.db.database import get_db 
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/my-tenant-info")
def get_tenant_info(request: Request,db: Session = Depends(get_db)):
    # You can access the state safely here!
    current_subdomain = request.state.subdomain 
    current_schema_name = request.state.schema_name
    
    return {
        "message": "You are currently inside your workspace.",
        "active_subdomain": current_subdomain, 
        "active_schema_name" : current_schema_name
    }