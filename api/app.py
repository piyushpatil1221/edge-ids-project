from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# =========================
# LOAD MODEL + SCALER
# =========================
model = joblib.load('../model/ids_model.pkl')
scaler = joblib.load('../model/scaler.pkl')

# 🔥 FIXED FEATURE LIST (MATCHES MODEL)
columns = [
    'duration','src_bytes','dst_bytes','count','srv_count',
    'serror_rate','srv_serror_rate','rerror_rate',
    'same_srv_rate','diff_srv_rate','dst_host_count',
    'dst_host_srv_count','dst_host_same_srv_rate',
    'dst_host_diff_srv_rate','dst_host_serror_rate'
]

# Encoding maps
protocol_map = {'icmp': 0, 'tcp': 1, 'udp': 2}
flag_map = {'SF': 0, 'S0': 1, 'REJ': 2}
service_map = {'http': 0, 'private': 1, 'other': 2}

@app.route('/')
def home():
    return "🚀 IDS API Running"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json.get('data')

        if data is None:
            return jsonify({"error": "No data provided"}), 400

        print("\n📥 RAW INPUT:", data)

        # =========================
        # CREATE DATAFRAME
        # =========================
        df = pd.DataFrame([data])

        # =========================
        # ENCODING
        # =========================
        df['protocol_type'] = df.get('protocol_type', 0)
        df['flag'] = df.get('flag', 0)
        df['service'] = df.get('service', 0)

        df['protocol_type'] = df['protocol_type'].map(protocol_map).fillna(0)
        df['flag'] = df['flag'].map(flag_map).fillna(0)
        df['service'] = df['service'].map(service_map).fillna(0)

        # =========================
        # NUMERIC CONVERSION
        # =========================
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.fillna(0, inplace=True)

        # =========================
        # MATCH MODEL FEATURES ONLY
        # =========================
        for col in columns:
            if col not in df:
                df[col] = 0

        df = df[columns]

        print("✅ FINAL INPUT:\n", df.head())

        # =========================
        # SCALING + PREDICTION
        # =========================
        scaled = scaler.transform(df.values)   # 🔥 FIXED
        pred = model.predict(scaled)[0]

        result = {
            "prediction": int(pred),
            "message": "🚨 Attack Detected" if pred == 1 else "✅ Normal Traffic"
        }

        print("🤖 RESULT:", result)

        return jsonify(result)

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)