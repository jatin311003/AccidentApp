import hashlib
import os
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URI'))
mongo_db = client['accidentDb']
users_collection = mongo_db['users']

# Blueprint setup
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


# ✅ Login Route
@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin(origin='http://localhost:3000', supports_credentials=True)
def login():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    login_details = request.get_json()

    user_from_db = users_collection.find_one({'email': login_details['email']})
    if not user_from_db:
        return jsonify({'msg': "User does not exist"}), 404

    encrypted_password = hashlib.sha256(login_details['password'].encode('utf-8')).hexdigest()
    if encrypted_password != user_from_db['password']:
        return jsonify({'msg': 'Incorrect password'}), 401

    access_token = create_access_token(identity=user_from_db['email'])

    return jsonify({
        "access_token": access_token,
        "user": {
            "email": user_from_db['email'],
            "username": user_from_db.get('username', 'No username provided')
        }
    }), 200


# ✅ Register Route
@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin(origin='http://localhost:3000', supports_credentials=True)
def register():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    new_user = request.get_json()
    new_user['password'] = hashlib.sha256(new_user["password"].encode('utf-8')).hexdigest()

    if users_collection.find_one({"username": new_user["username"]}):
        return jsonify({'msg': 'User already exists'}), 409

    users_collection.insert_one(new_user)
    return jsonify({'msg': 'User created successfully'}), 201
