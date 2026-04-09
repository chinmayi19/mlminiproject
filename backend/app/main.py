from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import predict

app = FastAPI()

# ✅ ADD THIS (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allows frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(predict.router)