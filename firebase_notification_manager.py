import heapq
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass
from utils.utils import compare_by_time
import firebase_admin
from firebase_admin import credentials
from firebase_admin.messaging import Message, Notification, send
from firebase_admin.exceptions import FirebaseError


class FirebaseNotificationManager:


    def __init__(self):
        self.MINIMUM_NOTIFICATION_DELAY = timedelta(hours=1)
        self.last_notification = {}
        self.heap = []
        self.cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(self.cred)

    def send_notification(self, topic):
        threading.Thread(target=self._send_notification, args=(topic,)).start()

    def _send_notification(self, topic, title="watafaq", body="watafaq"):
        print(topic)
        topic = topic.replace(" ","_")
        now = datetime.now()
        prev = None
        try:
            if self._check_last_topic_notification(topic):
                if topic in self.last_notification:
                    prev = self.last_notification[topic]
                self.last_notification[topic] = now
                send(Message(
                    notification=Notification(title=title, body=body),
                    topic=topic
                ))
                print("hi i send notifications")
        except (ValueError, FirebaseError) as e:
            self.last_notification[topic] = prev
            if prev is None:
                del self.last_notification[topic]
            print(f"Notification failed with error:\n{e}")

    def _check_last_topic_notification(self, topic):
        print(self.last_notification)
        if topic not in self.last_notification:
            print("check line 1")
            return True
        elif datetime.now() - self.last_notification[topic] > self.MINIMUM_NOTIFICATION_DELAY:
            print("check line 2")
            return True
        else:
            print("check line 3")
            return False

    def add_item_to_schedule(self,data):
        pass

