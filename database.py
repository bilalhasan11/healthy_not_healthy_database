# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import os
from database import init_db, save_prediction, get_history

app = Flask(__name__)
CORS(app)

# Initialize the database on startup
init_db()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        audio_name = audio_file.filename
        audio_data = audio_file.read()  # Read audio file as binary
        possible_results = ["healthy", "not healthy", "try again"]
        result = random.choice(possible_results)

        # Save to database
        save_prediction(audio_name, result, audio_data)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def history():
    try:
        # Fetch history
        history = get_history()
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5010))
    app.run(debug=True, host='0.0.0.0', port=port)
