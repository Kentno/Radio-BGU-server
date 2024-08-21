import threading

from flask import Blueprint, jsonify, request
import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials
import dotenv
import os
from requests import request, get
from utils import *
from dotenv import load_dotenv
load_dotenv()

class AzuracastDataManager:
    def __init__(self,firebase_obj):
        self.firebase_obj = firebase_obj
        self._now_playing_url = "https://bguradio.co/api/nowplaying"
        self._apikey = os.environ.get('apiKey')
        self._broadcasters_url = "https://bguradio.co/api/station/1/streamers"  # Replace with your station URL

        self._data = self._get_data_from_azuracast()
        self._broadcasters = extract_broadcasters(self._data)
        self._upcoming = extract_upcoming(self._data,self.firebase_obj, init=True)

        self._running = True
        self._thread = threading.Thread(target=self._work_thread)
        self._thread.daemon = True  # Set thread as daemon
        self._thread.start()

    def _get_data_from_azuracast(self):
        # Combine client ID and secret for basic auth
        headers = {
            "Authorization": f"Bearer {self._apikey}"
        }
        # Send the request
        response = get(self._broadcasters_url, headers=headers)

        # Check for successful response
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            pass
    def _work_thread(self):
        while self._running:
            self._data = self._get_data_from_azuracast()
            self._broadcasters = extract_broadcasters(self._data)
            self._upcoming = extract_upcoming(self._data,self.firebase_obj)
            time.sleep(30)

    def get_broadcasters(self):
        return self._broadcasters

    def get_upcoming(self):
        return self._upcoming


# cred = credentials.Certificate("app_server/bgu-radio-server/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)
#
#
# def send_all():
#     # [START send_all]
#     # Create a list containing up to 500 messages.
#
#     messages = [
#         messaging.Message(
#             notification=messaging.Notification('עלינו לשידור חי', extrat_song_title(get_response())),
#             topic="Radio"
#         )
#     ]
#
#     response = messaging.send(messages[0])
#     # See the BatchResponse reference documentation
#     # for the contents of response.
#     print('{0} messages were sent successfully'.format(response.success_count))
#     # [END send_all]


# Define a function to periodically check the condition
# def check_and_call():
#     # Check the condition every 5 seconds
#     while True:
#         if not check_condition():
#             print("")
#             # send_all()  # Call func() if condition is True
#         else:
#             print(extract_song_name(get_response()))
#         time.sleep(600)  # Sleep for 600 seconds before checking again


# # Create a thread to run the check_and_call function
# thread = threading.Thread(target=check_and_call)
# thread.daemon = True  # Set the thread as a daemon so it exits when the main program exits
# thread.start()

# Main program (can be empty or do other tasks while the thread runs)
# try:
#     while True:
#         time.sleep(60)  # Keep the main thread alive
# except KeyboardInterrupt:
#     print("Exiting...")


