from fastapi import FastAPI
from app.routes import predict

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend is working"}

app.include_router(predict.router)