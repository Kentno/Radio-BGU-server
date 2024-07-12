import heapq
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass
from utils import compare_by_time
import firebase_admin
from firebase_admin import credentials
from firebase_admin.messaging import Message, Notification, send
from firebase_admin.exceptions import FirebaseError


class FirebaseNotificationManager:

    def __init__(self):
        self.MINIMUM_NOTIFICATION_DELAY = timedelta(hours=1)
        self.last_notification = datetime.now() - timedelta(hours=2)
        self.heap = []
        self.cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(self.cred)

    def send_notification(self, broadcast):
        threading.Thread(target=self._send_notification, args=(broadcast, broadcast[0], broadcast[1],)).start()

    def _send_notification(self, broadcast, title="default", body="default"):
        print(broadcast)
        broadcast = [x.replace(" ", "_") for x in broadcast if type(x) is str]
        now = datetime.now()
        prev = None
        try:
            if self._check_last_broadcast_notification(broadcast):
                prev, self.last_notification = self.last_notification, now
                send(Message(
                    notification=Notification(title=title, body=body),
                    topic="live"
                ))
                print("hi i send notifications")
        except (ValueError, FirebaseError) as e:
            self.last_notification = prev
            if prev is None:
                self.last_notification = datetime.now() - timedelta(hours=1)
            print(f"Notification failed with error:\n{e}")

    def _check_last_broadcast_notification(self, broadcast):
        if datetime.now() > self.last_notification + self.MINIMUM_NOTIFICATION_DELAY:
            return True
        else:
            return False
        # print(self.last_notification)
        # if broadcast not in self.last_notification:
        #     print("check line 1")
        #     return True
        # elif datetime.now() - self.last_notification[broadcast] > self.MINIMUM_NOTIFICATION_DELAY:
        #     print("check line 2")
        #     return True
        # else:
        #     print("check line 3")
        #     return False

    def add_item_to_schedule(self, data):
        pass
