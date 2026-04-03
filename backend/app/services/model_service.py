import joblib
import numpy as np

# Load models (make sure path is correct)
model_o1 = joblib.load("models/random_forest_model_o1.pkl")
model_main = joblib.load("models/random_forest_model.pkl")
scaler = joblib.load("models/scaler.pkl")


# Convert perception → numeric
def convert_to_numeric(perceptions):
    score_map = {
        "True": 1,
        "Mostly True": 0.5,
        "Mixture": 0,
        "Mostly False": -0.5,
        "False": -1
    }

    values = []
    for p in perceptions:
        p = str(p).strip().title()
        values.append(score_map.get(p, 0))  # default = 0

    return np.array(values)


# Extract statistical features
def extract_features(values):
    mean = np.mean(values)
    median = np.median(values)
    variance = np.var(values)

    # Safe skew calculation
    if len(values) < 3:
        skew = 0
    else:
        skew = float(np.mean((values - mean) ** 3))

    return [mean, median, variance, skew]


# MAIN FUNCTION (used in API)
def analyze_claim_with_model(perceptions):
    # Step 1: Convert to numeric
    values = convert_to_numeric(perceptions)

    # Safety check
    if len(values) == 0:
        return {
            "O1_prediction": "Unknown",
            "Main_prediction": "Low",
            "features": {
                "mean": 0,
                "median": 0,
                "variance": 0,
                "skew": 0
            }
        }

    # Step 2: Extract features
    features = extract_features(values)

    # Step 3: Scale features
    features_scaled = scaler.transform([features])

    # Step 4: Model predictions
    o1_pred = model_o1.predict(features_scaled)
    main_pred = model_main.predict(features_scaled)

    # Step 5: Convert outputs properly (NO int conversion ❌)
    o1_result = str(o1_pred[0])
    main_result = str(main_pred[0])

    # OPTIONAL: normalize TPB output
    # If your model outputs True/False instead of High/Low
    if main_result not in ["High", "Low"]:
        main_result = "High" if main_result == "True" else "Low"

    return {
        "O1_prediction": o1_result,      # "True" / "False"
        "Main_prediction": main_result, # "High" / "Low"
        "features": {
            "mean": float(features[0]),
            "median": float(features[1]),
            "variance": float(features[2]),
            "skew": float(features[3])
        }
    }