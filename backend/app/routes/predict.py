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

                # Get claim text
                match = claims_df.loc[
                    claims_df["claim_id"] == claim_id, "claim"
                ]
                claim_text = match.values[0] if len(match) > 0 else "Unknown"

                # ✅ Convert model outputs to labels
                predicted_truth = "False" if str(output["O1_prediction"]) in ["0", "False"] else "True"
                predicted_TPB = "High" if str(output["Main_prediction"]) in ["1", "High"] else "Low"

                results.append({
                    "claim_id": int(claim_id),
                    "claim": str(claim_text),
                    "predicted_truth": predicted_truth,
                    "predicted_TPB": predicted_TPB,
                    "disputability": float(output["features"]["variance"])
                })

            except Exception as e:
                print(f"Error processing claim {claim_id}: {e}")

        # Step 4: Convert to DataFrame
        df = pd.DataFrame(results)

        # Step 5: TPB score mapping
        df["tpb_score"] = df["predicted_TPB"].map({
            "High": 1,
            "Low": 0
        })

        # Step 6: Categorization

        # O1 → False claims
        false_claims = df[df["predicted_truth"] == "False"] \
            .sort_values(by="disputability", ascending=False)

        # O2 → Most misperceived
        misperceived = df[
            (df["predicted_TPB"] == "High") &
            (df["predicted_truth"] != "False")
        ].sort_values(by=["tpb_score", "disputability"], ascending=[False, False])

        # O3 → Most disputed (PURE variance)
        disputed = df.sort_values(by="disputability", ascending=False)

        # Step 7: Return JSON-safe output
        return {
            "false_claims": [
                {
                    "claim_id": int(row["claim_id"]),
                    "claim": str(row["claim"]),
                    "predicted_truth": str(row["predicted_truth"]),
                    "predicted_TPB": str(row["predicted_TPB"]),
                    "disputability": float(row["disputability"])
                }
                for _, row in false_claims.iterrows()
            ],
            "most_misperceived_claims": [
                {
                    "claim_id": int(row["claim_id"]),
                    "claim": str(row["claim"]),
                    "predicted_truth": str(row["predicted_truth"]),
                    "predicted_TPB": str(row["predicted_TPB"]),
                    "disputability": float(row["disputability"])
                }
                for _, row in misperceived.iterrows()
            ],
            "most_disputed_claims": [
                {
                    "claim_id": int(row["claim_id"]),
                    "claim": str(row["claim"]),
                    "predicted_truth": str(row["predicted_truth"]),
                    "predicted_TPB": str(row["predicted_TPB"]),
                    "disputability": float(row["disputability"])
                }
                for _, row in disputed.iterrows()
            ]
        }

    except Exception as e:
        return {"error": str(e)}