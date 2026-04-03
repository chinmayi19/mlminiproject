from fastapi import APIRouter
from app.schemas.input_schema import NewsInput
from app.services.model_service import analyze_claim_with_model
from app.schemas.input_schema import ClaimRequest

router = APIRouter()

@router.post("/analyze_claim")
def analyze_claim(data: ClaimRequest):
    result = analyze_claim_with_model(data.perceptions)

    return {
        "claim_id": data.claim_id,
        "result": result,
        "status": "success"
    }