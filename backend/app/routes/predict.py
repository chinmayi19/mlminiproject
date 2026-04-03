from fastapi import APIRouter, UploadFile, File
import pandas as pd
from app.services.model_service import analyze_claim_with_model

router = APIRouter()


@router.post("/analyze_dataset")
async def analyze_dataset(
    claims_file: UploadFile = File(...),
    perceptions_file: UploadFile = File(...)
):
    # Step 1: Read CSV files
    claims_df = pd.read_csv(claims_file.file)
    perceptions_df = pd.read_csv(perceptions_file.file)

    # Step 2: Group perceptions by claim_id
    grouped = perceptions_df.groupby("claim_id")["perception"].apply(list)

    results = []

    # Step 3: Process each claim
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

    # Step 4: Convert to DataFrame
    df = pd.DataFrame(results)

    # Step 5: Add numeric TPB score (for correct sorting)
    df["tpb_score"] = df["predicted_TPB"].map({
        "High": 1,
        "Low": 0
    })

    # Step 6: Sorting for 3 objectives

    # O1 → False claims (sorted by disputability)
    false_claims = df[df["predicted_truth"] == "False"] \
        .sort_values(by="disputability", ascending=False)

    # O2 → Most misperceived (sorted by TPB score)
    misperceived = df.sort_values(by="tpb_score", ascending=False)

    # O3 → Most disputed (sorted by variance)
    disputed = df.sort_values(by="disputability", ascending=False)

    # Step 7: Return final output
    return {
        "false_claims": false_claims.to_dict(orient="records"),
        "most_misperceived_claims": misperceived.to_dict(orient="records"),
        "most_disputed_claims": disputed.to_dict(orient="records")
    }