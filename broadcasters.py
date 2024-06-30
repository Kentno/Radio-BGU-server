import flask
from flask import Blueprint, jsonify, request
#from app_server import azuracast_data_manager,utils
from managers.azuracast_data_manager import *
import __main__
streamers_bp = Blueprint('', __name__)


@streamers_bp.route("/broadcasters", methods=['GET'])
def getBroadcasters():
    """
    :return: a list of all active broadcasters for user topics(broadcasters) list
    """
    return __main__.azuracastDataManager.get_broadcasters()


@streamers_bp.route("/upcomingBroadcasts", methods=['GET'])
def upcomingBroadcast():
    """
    :return: Returns the three upcoming broadcasts as an edited string to display on the app news ticker
    """
    return __main__.azuracastDataManager.get_upcoming()


@streamers_bp.route("/send_firebase", methods=['GET'])
def sendFirebase():
    """
    :return: a list of all active broadcasters for user topics(broadcasters) list
    """
    topic = request.args.get("topic")
    __main__.firebase._send_notification(topic,"test","test")
    return jsonify(200)