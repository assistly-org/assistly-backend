# main.py  (now at ROOT level)
from fastapi import FastAPI


app = FastAPI(title="Clean Architecture Demo")

@app.get("/")
def server_status():
    return {"status":"Fast API Server Started ..."}
