import joblib
import numpy as np

# Load models
model_o1 = joblib.load("models/random_forest_model_o1.pkl")
model_main = joblib.load("models/random_forest_model.pkl")
scaler = joblib.load("models/scaler.pkl")


# Convert perception → number
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
        p = p.strip().title()
        values.append(score_map.get(p, 0))

    return np.array(values)   # ✅ IMPORTANT FIX


# Extract features
def extract_features(values):
    mean = np.mean(values)
    median = np.median(values)
    variance = np.var(values)

    # safe skew
    skew = 0 if len(values) < 3 else float(np.mean((values - mean) ** 3))

    return [mean, median, variance, skew]


# MAIN FUNCTION
def analyze_claim_with_model(perceptions):
    values = convert_to_numeric(perceptions)
    features = extract_features(values)

    features_scaled = scaler.transform([features])

    o1_pred = model_o1.predict(features_scaled)
    main_pred = model_main.predict(features_scaled)

    return {
        "O1_prediction": int(o1_pred[0]),
        "Main_prediction": int(main_pred[0]),
        "features": {
            "mean": features[0],
            "median": features[1],
            "variance": features[2],
            "skew": features[3]
        }
    }