from fastapi import APIRouter, UploadFile, File
import pandas as pd
from app.services.model_service import analyze_claim_with_model

router = APIRouter()


@router.post("/analyze_dataset")
async def analyze_dataset(
    claims_file: UploadFile = File(...),
    perceptions_file: UploadFile = File(...)
):
    try:
        # Step 1: Read CSV files
        claims_df = pd.read_csv(claims_file.file)
        perceptions_df = pd.read_csv(perceptions_file.file)

        # Step 2: Group perceptions by claim_id
        grouped = perceptions_df.groupby("claim_id")["perception"].apply(list)

        results = []

        # Step 3: Process each claim
        for claim_id, perceptions in grouped.items():
            try:
                output = analyze_claim_with_model(perceptions)

                # Safe claim fetch
                match = claims_df.loc[
                    claims_df["claim_id"] == claim_id, "claim"
                ]
                claim_text = match.values[0] if len(match) > 0 else "Unknown"

                results.append({
                    "claim_id": int(claim_id),
                    "claim": claim_text,
                    "predicted_truth": output["O1_prediction"],   # already "True"/"False"
                    "predicted_TPB": output["Main_prediction"],   # already "High"/"Low"
                    "disputability": output["features"]["variance"]
                })

            except Exception as e:
                print(f"Error processing claim {claim_id}: {e}")

        # Step 4: Convert to DataFrame
        df = pd.DataFrame(results)

        # Step 5: Add numeric TPB score for sorting
        df["tpb_score"] = df["predicted_TPB"].map({
            "High": 1,
            "Low": 0
        })

        # Step 6: Apply sorting for 3 objectives

        # O1 → False claims sorted by disputability
        false_claims = df[df["predicted_truth"] == "False"] \
            .sort_values(by="disputability", ascending=False)

        # O2 → Most misperceived
        misperceived = df.sort_values(by="tpb_score", ascending=False)

        # O3 → Most disputed
        disputed = df.sort_values(by="disputability", ascending=False)

        # Step 7: Return clean output (without tpb_score)
        return {
            "false_claims": false_claims.drop(columns=["tpb_score"]).to_dict(orient="records"),
            "most_misperceived_claims": misperceived.drop(columns=["tpb_score"]).to_dict(orient="records"),
            "most_disputed_claims": disputed.drop(columns=["tpb_score"]).to_dict(orient="records")
        }

    except Exception as e:
        return {"error": str(e)}