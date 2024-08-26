from flask import Blueprint

# from app_server import azuracast_data_manager,utils
import __main__

streamers_bp = Blueprint('radio', __name__)


@streamers_bp.route("/broadcasters", methods=['GET'])
def get_broadcasters():
    """
    :return: a list of all active broadcasters for user topics(broadcasters) list
    """
    return __main__.azuracastDataManager.get_broadcasters()


@streamers_bp.route("/upcomingBroadcasts", methods=['GET'])
def upcoming_broadcast():
    """
    :return: Returns the three upcoming broadcasts as an edited string to display on the app news ticker
    """
    return __main__.azuracastDataManager.get_upcoming()


@streamers_bp.route("/podcastList", methods=['GET'])
def get_podcast_data():
    return __main__.rss_feeds
