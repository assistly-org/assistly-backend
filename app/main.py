# main.py  (now at ROOT level)
from fastapi import FastAPI
from app.presentation.routes.user import router

app = FastAPI(title="Clean Architecture Demo")

@app.get("/")
def server_status():
    return {"status":"Fast API Server Started ..."}
app.include_router(router, prefix="/api")