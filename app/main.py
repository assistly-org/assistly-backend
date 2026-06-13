from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, Depends # <-- Import Depends
from sqlalchemy.orm import Session
from fastapi import FastAPI
from app.presentation.middleware.tenant_middlewares.tenant_middleware import SubdomainTenantMiddleware
from app.presentation.routers.tenants import tenant_route
from app.presentation.routers.auth import auth_service


app = FastAPI(title="Assistly API")

app.add_middleware(SubdomainTenantMiddleware)
app.include_router(tenant_route.router)
app.include_router(auth_service.router)

# db: Session = Depends(get_db)
# Inject the DB dependency here!
@app.get("/")
def server_status():
    # The moment FastAPI tries to inject 'db' here, it runs get_db(), 
    # attempts to switch the schema, fails, and throws your 404!
    return {"status":"Fast API Server Started ..."}