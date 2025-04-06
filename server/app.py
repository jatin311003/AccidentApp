import os
import datetime
from flask import Flask, jsonify, send_from_directory
from flask_mail import Mail
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
print("JWT_SECRET_KEY from env:", os.getenv('JWT_SECRET_KEY'))
# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'static/videos'

# ✅ Enable CORS
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# ✅ MongoDB setup
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
mongo_db = client['accidentDb']
users_collection = mongo_db.users
accidents_collection = mongo_db.accidents

# ✅ JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
jwt = JWTManager(app)

# ✅ Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# ✅ Cloudinary Configuration
import cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('API_KEY'),
    api_secret=os.getenv('API_SECRET')
)

# ✅ Register Blueprints
from blueprints.auth.auth import auth_bp
from blueprints.accident.accident import accident_bp
from blueprints.public.public import public_bp
from blueprints.emails.emails import emails

app.register_blueprint(auth_bp)
app.register_blueprint(accident_bp)
app.register_blueprint(public_bp)
app.register_blueprint(emails)

# ✅ Root route to verify server status
@app.route('/')
def home():
    return jsonify({"msg": "Server is running successfully!"})

# ✅ Serve static files (if needed)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# ✅ Run the Flask app
if __name__ == '__main__':app.run(debug=True, port=8080)


