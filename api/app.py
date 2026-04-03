from flask import Flask, request, jsonify
import joblib
import numpy as np
import pickle
import pandas as pd

app = Flask(__name__)

# Load model
model = joblib.load('../model/ids_model.pkl')

# Load columns
columns = pickle.load(open('../model/columns.pkl', 'rb'))

@app.route('/')
def home():
    return "🚀 IDS API Running"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json['data']

        # Convert to dataframe
        temp_df = pd.DataFrame([data])

        # One-hot encoding
        temp_df = pd.get_dummies(temp_df)

        # Create full structure
        df = pd.DataFrame(columns=columns)

        # Merge safely
        df = pd.concat([df, temp_df], axis=0).fillna(0)

        # Match column order
        df = df[columns]

        # Convert to numpy
        df = df.values

        prediction = model.predict(df)

        return jsonify({
            "prediction": int(prediction[0]),
            "message": "Attack Detected 🚨" if prediction[0] == 1 else "Normal Traffic ✅"
        })

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)