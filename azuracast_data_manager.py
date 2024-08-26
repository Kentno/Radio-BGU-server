import json
import os
import threading
from time import sleep

from dotenv import load_dotenv
from requests import get

from utils import *

load_dotenv()


class AzuracastDataManager:
    def __init__(self, firebase_obj):
        self.firebase_obj = firebase_obj
        self._now_playing_url = "https://bguradio.co/api/nowplaying"
        self._apikey = os.environ.get('apiKey')
        self._broadcasters_url = "https://bguradio.co/api/station/1/streamers"  # Replace with your station URL

        self._data = self._get_data_from_azuracast()
        self._broadcasters = extract_broadcasters(self._data)
        self._upcoming = extract_upcoming(self._data, self.firebase_obj, init=True)

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
            self._upcoming = extract_upcoming(self._data, self.firebase_obj)
            sleep(30)

    def get_broadcasters(self):
        return self._broadcasters

    def get_upcoming(self):
        return self._upcoming
