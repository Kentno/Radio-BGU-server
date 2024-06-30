from flask import Flask
from flask_cors import CORS
# from app_serverd.routes.broadcasters import streamers_bp
from routes.broadcasters import streamers_bp
from managers.azuracast_data_manager import AzuracastDataManager
from managers.firebase_notification_manager import FirebaseNotificationManager

app = Flask(__name__)
CORS(app, supports_credentials=True)
firebase = FirebaseNotificationManager()
azuracastDataManager = AzuracastDataManager()
app.register_blueprint(streamers_bp)

@app.route('/')
def home():
    return 'Hello, World!'


if __name__ == "__main__":
    app.run(debug=True)
