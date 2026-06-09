from fastapi import FastAPI, Depends # <-- Import Depends
from sqlalchemy.orm import Session
from app.presentation.middleware.tenant_middleware import SubdomainTenantMiddleware
from app.infrastructure.db.database import get_db # <-- Import your DB dependency

app = FastAPI(title="Assistly API")

app.add_middleware(SubdomainTenantMiddleware)

# Inject the DB dependency here!
@app.get("/")
def server_status(db: Session = Depends(get_db)):
    # The moment FastAPI tries to inject 'db' here, it runs get_db(), 
    # attempts to switch the schema, fails, and throws your 404!
    return {"status":"Fast API Server Started ..."}