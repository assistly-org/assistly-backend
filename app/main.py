from dotenv import load_dotenv
load_dotenv() 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from app.presentation.routers.analytics import analytics_route

from app.presentation.middleware.tenant_middlewares.tenant_middleware import SubdomainTenantMiddleware
from app.presentation.routers.tenants import tenant_route
from app.presentation.routers.auth import auth_service
from app.presentation.routers.websocket.chat import router as websocket_router

# In main.py - at the top:
from app.presentation.routers.agent import agent
from app.presentation.routers.tenants import organizations
# Down below where you include it:
app = FastAPI(title="Assistly API")


# ⚡ Middleware Order Note:
# You actually did this perfectly! By adding CORSMiddleware LAST,
# FastAPI makes it run FIRST on incoming requests. This ensures your
# browser's preflight OPTIONS requests aren't blocked by your Tenant Bouncer!
app.add_middleware(SubdomainTenantMiddleware)
app.include_router(websocket_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://mobilemart.localhost:3000",
    ],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent.router)
app.include_router(tenant_route.router)
app.include_router(auth_service.router)
app.include_router(analytics_route.router)
app.include_router(organizations.router)


@app.get("/")
def server_status():
    return {"status": "Assistly API Server Started & Running ..."}