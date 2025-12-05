import os
import datetime
from flask import Flask, jsonify, send_from_directory
from flask_mail import Mail
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from dotenv import load_dotenv

from flask import request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl

# Load environment variables from .env file
load_dotenv()
print("JWT_SECRET_KEY from env:", os.getenv('JWT_SECRET_KEY'))
# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'static/videos'

# ✅ Enable CORS for web + mobile
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

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


@app.route('/api/mobile/sos', methods=['POST'])
def mobile_sos():
    try:
        data = request.get_json(force=True)
        print("Received mobile SOS data:", data)

        # Validate
        required_fields = ['userId', 'lat', 'lng', 'speedKmph', 'accelG']
        for f in required_fields:
            if f not in data:
                return jsonify({"ok": False, "error": f"Missing field {f}"}), 400

        # Insert into MongoDB
        mongo_db.mobile_alerts.insert_one({
            "userId": data['userId'],
            "lat": data['lat'],
            "lng": data['lng'],
            "speedKmph": data['speedKmph'],
            "accelG": data['accelG'],
            "timestamp": datetime.datetime.utcnow().isoformat()
        })

        # --- Send Email Alert ---
        sender = app.config['MAIL_USERNAME']
        receiver = data.get('email', sender)  # or pick from user profile
        subject = "🚨 Accident Detected by AccidentApp"
        maps_link = f"https://www.google.com/maps?q={data['lat']},{data['lng']}"

        html = f"""
        <h3>Possible Accident Detected</h3>
        <p><b>User ID:</b> {data['userId']}</p>
        <p><b>Location:</b> <a href="{maps_link}">{maps_link}</a></p>
        <p><b>Speed:</b> {data['speedKmph']} km/h<br>
        <b>Impact:</b> {data['accelG']} g</p>
        <p>Timestamp: {datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}</p>
        """

        # Create email
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = receiver
        message.attach(MIMEText(html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, app.config['MAIL_PASSWORD'])
            server.sendmail(sender, receiver, message.as_string())

        print("✅ SOS email sent successfully!")
        return jsonify({"ok": True, "message": "SOS processed successfully"}), 200

    except Exception as e:
        print("❌ Error handling SOS:", e)
        return jsonify({"ok": False, "error": str(e)}), 500

# ✅ Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)


