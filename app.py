from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from database import init_db, save_prediction, get_history, register_user, authenticate_user

app = Flask(__name__)
CORS(app)
init_db()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    return register_user(data['username'], data['password'])

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    return authenticate_user(data['username'], data['password'])

@app.route('/predict', methods=['POST'])
def predict():
    if 'audio' not in request.files or 'user_id' not in request.form:
        return jsonify({"error": "Missing data"}), 400
    
    user_id = request.form['user_id']
    audio_file = request.files['audio']
    result = random.choice(["healthy", "not healthy", "try again"])

    save_prediction(user_id, audio_file.filename, result, audio_file.read())
    return jsonify({"result": result})

@app.route('/history', methods=['GET'])
def history():
    user_id = request.args.get('user_id')
    return jsonify({"history": get_history(user_id)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5010)
