from flask import Flask, request, jsonify
import joblib
import pickle
import pandas as pd

app = Flask(__name__)

# =========================
# LOAD MODEL + FILES
# =========================
model = joblib.load('../model/ids_model.pkl')
scaler = joblib.load('../model/scaler.pkl')

columns = pickle.load(open('../model/columns.pkl', 'rb'))

# 🔥 REMOVE unwanted columns
columns = [col for col in columns if col not in ['level', 'attack']]

# =========================
# FULL 41 FEATURES
# =========================
full_columns = [
    'duration','protocol_type','service','flag','src_bytes','dst_bytes',
    'land','wrong_fragment','urgent','hot','num_failed_logins','logged_in',
    'num_compromised','root_shell','su_attempted','num_root',
    'num_file_creations','num_shells','num_access_files',
    'num_outbound_cmds','is_host_login','is_guest_login','count',
    'srv_count','serror_rate','srv_serror_rate','rerror_rate',
    'srv_rerror_rate','same_srv_rate','diff_srv_rate',
    'srv_diff_host_rate','dst_host_count','dst_host_srv_count',
    'dst_host_same_srv_rate','dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate','dst_host_srv_diff_host_rate',
    'dst_host_serror_rate','dst_host_srv_serror_rate',
    'dst_host_rerror_rate','dst_host_srv_rerror_rate'
]

# =========================
# ENCODING MAPS
# =========================
protocol_map = {'icmp': 0, 'tcp': 1, 'udp': 2}

flag_map = {
    'SF': 0, 'S0': 1, 'REJ': 2, 'RSTR': 3, 'RSTO': 4,
    'SH': 5, 'S1': 6, 'S2': 7, 'S3': 8
}

service_map = {
    'http': 0, 'private': 1, 'ftp_data': 2, 'eco_i': 3,
    'telnet': 4, 'smtp': 5, 'ftp': 6,
    'domain_u': 7, 'other': 8, 'ecr_i': 9
}

@app.route('/')
def home():
    return "🚀 IDS API Running"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json.get('data')

        if data is None:
            return jsonify({"error": "No data provided"}), 400

        # =========================
        # CREATE FULL DATAFRAME (41)
        # =========================
        temp_df = pd.DataFrame([data], columns=full_columns)

        # =========================
        # NUMERIC CONVERSION
        # =========================
        for col in temp_df.columns:
            if col not in ['protocol_type', 'service', 'flag']:
                temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce')

        # =========================
        # ENCODING
        # =========================
        temp_df['protocol_type'] = temp_df['protocol_type'].map(protocol_map)
        temp_df['flag'] = temp_df['flag'].map(flag_map)
        temp_df['service'] = temp_df['service'].map(service_map)

        temp_df.fillna(0, inplace=True)

        # =========================
        # 🔥 ONLY SELECT 15 FEATURES (THIS IS THE FIX)
        # =========================
        temp_df = temp_df[columns]

        # =========================
        # SCALING (NOW MATCHES)
        # =========================
        df_scaled = scaler.transform(temp_df.values)

        # =========================
        # PREDICTION
        # =========================
        prediction = model.predict(df_scaled)

        return jsonify({
            "prediction": int(prediction[0]),
            "message": "🚨 Attack Detected" if prediction[0] == 1 else "✅ Normal Traffic"
        })

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)