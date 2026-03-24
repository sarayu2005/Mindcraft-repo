from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Ensure models exist before loading
if not os.path.exists('models/rf_model.pkl'):
    print("❌ ERROR: Models not found. Please run 'python train_model.py' first.")
    exit()

print("🔌 MINDCRAFT Server v2 Online. Loading Neural Link...")
scaler = joblib.load('models/scaler.pkl')
rf_model = joblib.load('models/rf_model.pkl')
profile_map = joblib.load('models/profile_map.pkl')
print("✅ Models Loaded Successfully.")

@app.route('/predict_profile', methods=['POST'])
def predict():
    data = request.json
    print(f"📥 Received Player Telemetry: {data}")

    try:
        # 1. Parse Input (Mapping frontend JSON to model features correctly)
        input_data = {
            's1_learn_mode': int(data['s1']),
            's2_prob_solve': int(data['s2']),
            's3_content': int(data['s3']),
            's4_pacing': int(data['s4']),
            's5_repetition': int(data['s5']),
            's6_skill_lvl': int(data['s6']),
            'trace_latency': float(data['trace_time']),
            'trace_accuracy': int(data['trace_correct']),
            'debug_attempts': int(data['debug_runs']),
            'hint_usage': int(data['hint_used'])
        }
        
        input_vector = pd.DataFrame([input_data])

        # 2. Scale Data
        X_new = scaler.transform(input_vector)

        # 3. Predict
        cluster_id = rf_model.predict(X_new)[0]
        profile_name = profile_map[cluster_id]
        confidence = max(rf_model.predict_proba(X_new)[0])

        response = {
            "profile": profile_name,
            "confidence": int(confidence * 100),
            "status": "success"
        }
        print(f"📤 Prediction Sent: {response['profile']} ({response['confidence']}%)")
        return jsonify(response)

    except Exception as e:
        print(f"❌ Inference Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)