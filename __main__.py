from flask import Flask
from flask_cors import CORS
# from app_serverd.routes.broadcasters import streamers_bp
# from broadcasters import streamers_bp
from azuracast_data_manager import AzuracastDataManager
from firebase_notification_manager import FirebaseNotificationManager
from utils import load_rss_feed, read_rss_links
import configparser

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route('/')
def home():
    return 'Hello, World!'


@app.route("/broadcasters", methods=['GET'])
def getBroadcasters():
    """
    :return: a list of all active broadcasters for user topics(broadcasters) list
    """
    return azuracastDataManager.get_broadcasters()


@app.route("/upcomingBroadcasts", methods=['GET'])
def upcomingBroadcast():
    """
    :return: Returns the three upcoming broadcasts as an edited string to display on the app news ticker
    """
    return azuracastDataManager.get_upcoming()


@app.route("/podcastList", methods=['GET'])
def getPodcastData():
    return rss_feeds


if __name__ == "__main__":

    firebase = FirebaseNotificationManager()
    azuracastDataManager = AzuracastDataManager(firebase)
    # app.register_blueprint(streamers_bp)
    podcast_data = []
    config = configparser.ConfigParser()
    config.read('config.ini')
    rss_links_path = config['RSS'].get('path')
    urls = read_rss_links(rss_links_path)
    rss_feeds = [load_rss_feed(url) for url in urls]


    app.run(host='0.0.0.0', port=5001)
