from flask import Flask
from flask_cors import CORS
# from app_serverd.routes.broadcasters import streamers_bp
from broadcasters import streamers_bp
from azuracast_data_manager import AzuracastDataManager
from firebase_notification_manager import FirebaseNotificationManager
from utils import load_rss_feed, read_rss_links
import configparser

app = Flask(__name__)
CORS(app, supports_credentials=True)
firebase = FirebaseNotificationManager()
azuracastDataManager = AzuracastDataManager()
app.register_blueprint(streamers_bp)
podcast_data = []
config = configparser.ConfigParser()
config.read('config.ini')
rss_links_path = config['RSS'].get('path')
rss_feeds = []

@app.route('/')
def home():
    return 'Hello, World!'


if __name__ == "__main__":
    urls = read_rss_links(rss_links_path)
    rss_feeds = [load_rss_feed(url) for url in urls]


    app.run(debug=True, host='0.0.0.0', port=5001)
