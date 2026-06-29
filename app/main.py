from dotenv import load_dotenv
load_dotenv() 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from app.presentation.routers.analytics import analytics_route

from app.presentation.middleware.tenant_middlewares.tenant_middleware import SubdomainTenantMiddleware
from app.presentation.routers.tenants import tenant_route
from app.presentation.routers.auth import auth_service
from app.presentation.routers.websocket.chat import router as websocket_router

app = FastAPI(title="Assistly API")

app.add_middleware(SubdomainTenantMiddleware)
app.include_router(websocket_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tenant_route.router)
app.include_router(auth_service.router)
app.include_router(analytics_route.router)
for route in app.routes:
    print(f"Route: {route.path}")

@app.get("/")
def server_status():
    return {"status": "Assistly API Server Started & Running ..."}