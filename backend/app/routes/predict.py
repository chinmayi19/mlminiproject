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
        # Step 1
        claims_df = pd.read_csv(claims_file.file)
        perceptions_df = pd.read_csv(perceptions_file.file)

        # Step 2
        grouped = perceptions_df.groupby("claim_id")["perception"].apply(list)

        results = []

        # Step 3
        for claim_id, perceptions in grouped.items():
            try:
                output = analyze_claim_with_model(perceptions)

                match = claims_df.loc[
                    claims_df["claim_id"] == claim_id, "claim"
                ]
                claim_text = match.values[0] if len(match) > 0 else "Unknown"

                results.append({
                    "claim_id": int(claim_id),
                    "claim": claim_text,
                    "predicted_truth": output["O1_prediction"],
                    "predicted_TPB": output["Main_prediction"],
                    "disputability": output["features"]["variance"]
                })

            except Exception as e:
                print(f"Error processing claim {claim_id}: {e}")

        # Step 4
        df = pd.DataFrame(results)

        # Step 5
        df["tpb_score"] = df["predicted_TPB"].map({
            "High": 1,
            "Low": 0
        })

        # ✅ Step 6 (INSIDE TRY — IMPORTANT)

        false_claims = df[df["predicted_truth"] == "False"] \
            .sort_values(by="disputability", ascending=False)

        misperceived = df[
            (df["predicted_TPB"] == "High") &
            (df["predicted_truth"] != "False")
        ].sort_values(by="tpb_score", ascending=False)

        disputed = []

        # Step 7
        return {
            "false_claims": false_claims.drop(columns=["tpb_score"]).to_dict(orient="records"),
            "most_misperceived_claims": misperceived.drop(columns=["tpb_score"]).to_dict(orient="records"),
            "most_disputed_claims": disputed
        }

    except Exception as e:
        return {"error": str(e)}