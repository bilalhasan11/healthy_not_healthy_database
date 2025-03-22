from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from googleapiclient.discovery import build
from google.oauth2 import service_account
from database import (
    init_db, save_prediction, get_history, register_user, authenticate_user,
    get_user_profile, update_user_profile, get_farm_details_from_db, update_farm_details_in_db,get_farm_detailss_from_db,get_hives_from_db,get_hive_detail_from_db
)

app = Flask(__name__)
CORS(app)
init_db()

# Google Drive API Setup
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Ensure this file is in your project directory
FOLDER_ID = '1rit57aSKEnPquEDv0ysG_3t9VFd1mhqr'  # Replace with your actual Google Drive folder ID

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

def upload_to_drive(audio_file):
    """Uploads a file to Google Drive and returns the file ID."""
    file_metadata = {
        'name': audio_file.filename,
        'parents': [FOLDER_ID]
    }
    
    media = {'media_body': audio_file, 'mimetype': audio_file.content_type}
    
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media['media_body'],
        fields='id'
    ).execute()
    
    return file.get('id')

@app.route('/predict', methods=['POST'])
def predict():
    if 'audio' not in request.files or 'user_id' not in request.form:
        return jsonify({"error": "Missing data"}), 400

    user_id = request.form['user_id']
    audio_file = request.files['audio']
    result = random.choice(["healthy", "not healthy", "try again"])

    save_prediction(user_id, audio_file.filename, result, audio_file.read())
    return jsonify({"result": result})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    return register_user(data['fullName'], data['email'], data['password'])

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    return authenticate_user(data['email'], data['password'])

@app.route('/profile', methods=['GET'])
def profile():
    user_id = request.args.get('user_id')
    return jsonify(get_user_profile(user_id))

@app.route('/profile/update', methods=['POST'])
def update_profile():
    data = request.json
    return jsonify(update_user_profile(
        data['user_id'], data['fullname'], data['country'], data['city'], data['gender'], data['phone_number']
    ))

@app.route('/history', methods=['GET'])
def history():
    user_id = request.args.get('user_id')
    return jsonify({"history": get_history(user_id)})

@app.route('/farm', methods=['GET'])
def get_farm_details():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    farm = get_farm_details_from_db(user_id)
    return jsonify(farm) if farm else jsonify({"error": "Farm details not found"}), 404

@app.route('/farm/update', methods=['POST'])
def update_farm():
    data = request.json
    return jsonify(update_farm_details_in_db(
        data['user_id'], data['fullname'], data['country'], data['city'], data['zip']
    ))
@app.route('/farms', methods=['GET'])
def get_farm():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    farm = get_farm_details_from_db(user_id)
    return jsonify(farm) if farm else jsonify({"error": "No farm registered"}), 404

@app.route('/hives', methods=['GET'])
def get_hives():
    farm_id = request.args.get('farm_id')
    if not farm_id:
        return jsonify({"error": "Farm ID is required"}), 400

    hives = get_hives_from_db(farm_id)
    return jsonify(hives)
    
@app.route('/hive_detail', methods=['GET'])
def get_hives_detail():
    hive_id = request.args.get('hive_id')
    if not hive_id:
        return jsonify({"error": "Hive Id is required"}), 400

    hivess = get_hive_detail_from_db(hive_id)
    return jsonify(hivess)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5010)
