from fastapi import APIRouter, UploadFile, File
import pandas as pd
from app.services.model_service import analyze_claim_with_model

router = APIRouter()

@router.post("/analyze_dataset")
async def analyze_dataset(
    claims_file: UploadFile = File(...),
    perceptions_file: UploadFile = File(...)
):
    # Read CSV files
    claims_df = pd.read_csv(claims_file.file)
    perceptions_df = pd.read_csv(perceptions_file.file)

    # Group perceptions by claim_id
    grouped = perceptions_df.groupby("claim_id")["perception"].apply(list)

    results = []

    for claim_id, perceptions in grouped.items():
        output = analyze_claim_with_model(perceptions)

        # Get claim text
        claim_text = claims_df.loc[
            claims_df["claim_id"] == claim_id, "claim"
        ].values[0]

        results.append({
            "claim_id": int(claim_id),
            "claim": claim_text,
            "predicted_truth": "False" if output["O1_prediction"] == 0 else "True",
            "predicted_TPB": "High" if output["Main_prediction"] == 1 else "Low",
            "disputability": output["features"]["variance"]
        })

    df = pd.DataFrame(results)

    # O1 → False claims
    false_claims = df[df["predicted_truth"] == "False"]

    # O2 → Most misperceived
    misperceived = df.sort_values(by="predicted_TPB", ascending=False)

    # O3 → Most disputed
    disputed = df.sort_values(by="disputability", ascending=False)

    return {
        "false_claims": false_claims.to_dict(orient="records"),
        "most_misperceived_claims": misperceived.to_dict(orient="records"),
        "most_disputed_claims": disputed.to_dict(orient="records")
    }