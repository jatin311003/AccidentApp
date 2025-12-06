import os
import datetime
import requests
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from dotenv import load_dotenv

# Load env vars
load_dotenv()
print("JWT_SECRET_KEY:", os.getenv("JWT_SECRET_KEY"))

# Flask app
app = Flask(__name__, static_folder="static")
app.config["UPLOAD_FOLDER"] = "static/videos"

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# MongoDB Atlas Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
mongo_db = client["accidentDb"]
users_collection = mongo_db.users
accidents_collection = mongo_db.accidents

# JWT Auth
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)
jwt = JWTManager(app)

# Cloudinary Config
import cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

# Import Blueprints
from blueprints.auth.auth import auth_bp
from blueprints.accident.accident import accident_bp
from blueprints.public.public import public_bp
from blueprints.emails.emails import emails

app.register_blueprint(auth_bp)
app.register_blueprint(accident_bp)
app.register_blueprint(public_bp)
app.register_blueprint(emails)

# -----------------------------
# 🚀 BREVO EMAIL SENDER (NEW)
# -----------------------------
def send_brevo_mail(to_email, subject, html):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": os.getenv("BREVO_API_KEY")
    }

    payload = {
        "sender": {"name": "AccidentApp Alerts", "email": os.getenv("SENDER_EMAIL")},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html
    }

    response = requests.post(url, json=payload, headers=headers)
    print("📧 Brevo Response:", response.text)
    return response.status_code


# -----------------------------
# ROOT CHECK ROUTE
# -----------------------------
@app.route("/")
def home():
    return jsonify({"msg": "Server is running successfully!"})


# ------------------------------------
# 🚨 MOBILE SOS ALERT ENDPOINT
# ------------------------------------
@app.route("/api/mobile/sos", methods=["POST"])
def mobile_sos():
    try:
        data = request.get_json(force=True)
        print("📱 Received mobile SOS data:", data)

        # Validate
        required = ["userId", "lat", "lng", "speedKmph", "accelG"]
        for f in required:
            if f not in data:
                return jsonify({"ok": False, "error": f"Missing {f}"}), 400

        # Save to DB
        mongo_db.mobile_alerts.insert_one({
            "userId": data["userId"],
            "lat": data["lat"],
            "lng": data["lng"],
            "speedKmph": data["speedKmph"],
            "accelG": data["accelG"],
            "timestamp": datetime.datetime.utcnow().isoformat()
        })

        # Email Content
        maps_link = f"https://www.google.com/maps?q={data['lat']},{data['lng']}"
        html = f"""
        <h2>🚨 Accident Detected!</h2>
        <p><b>User:</b> {data['userId']}</p>
        <p><b>Location:</b> <a href="{maps_link}">{maps_link}</a></p>
        <p><b>Speed:</b> {data['speedKmph']} km/h</p>
        <p><b>Impact:</b> {data['accelG']} g</p>
        <p><b>Time:</b> {datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}</p>
        """

        # Send email using Brevo
        send_status = send_brevo_mail(
            os.getenv("SENDTO"),
            "🚨 Accident Detected by AccidentApp",
            html
        )

        print("📨 Email Status:", send_status)
        return jsonify({"ok": True, "message": "SOS processed"}), 200

    except Exception as e:
        print("❌ SOS Error:", e)
        return jsonify({"ok": False, "error": str(e)}), 500


# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
