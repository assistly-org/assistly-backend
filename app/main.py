from dotenv import load_dotenv
load_dotenv() 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

from app.presentation.middleware.tenant_middlewares.tenant_middleware import SubdomainTenantMiddleware
from app.presentation.routers.tenants import tenant_route
from app.presentation.routers.auth import auth_service

app = FastAPI(title="Assistly API")

# ⚡ Middleware Order Note: 
# You actually did this perfectly! By adding CORSMiddleware LAST, 
# FastAPI makes it run FIRST on incoming requests. This ensures your 
# browser's preflight OPTIONS requests aren't blocked by your Tenant Bouncer!
app.add_middleware(SubdomainTenantMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://mobilemart.localhost:3000" 
    ],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tenant_route.router)
app.include_router(auth_service.router)

@app.get("/")
def server_status():
    return {"status": "Assistly API Server Started & Running ..."}