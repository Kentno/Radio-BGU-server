import json
import time
import datetime
from xml.etree import ElementTree as ET

import requests

import __main__
from dataclasses import dataclass



@dataclass
class NotificationData:
    time: datetime
    details: dict


def get_all_streamers(data):
    ret = []
    for streamer in data:
        ret.append(streamer["streamer_username"])
    return ",".join(ret)


def extract_broadcasters(data):
    """
    :param data: json from azuracast/schedule
    :return: a list of strings, each string is a broadcaster name
    """
    broadcasters = []
    for streamer in data:
        broadcasters.append(streamer["display_name"])
    return broadcasters


def extract_upcoming(data,init=False):
    #TODO fix edge cases
    """
    return the 3 soonest broadcasts
    """
    upcomings = []
    unix_now = time.mktime(datetime.datetime.now().timetuple())
    for streamer in data:
        if len(streamer["schedule_items"]) == 0:
            continue
        streamer_name = streamer["display_name"]
        subject = streamer["comments"]
        for item in streamer["schedule_items"]:
            date = item["start_date"].split("-")
            if len(str(item["start_time"])) < 4:
                newtime = ("0"*(4-len(str(item["start_time"]))))+str(item["start_time"])
            else:
                newtime = str(item["start_time"])
            timeArr = [newtime[i:i + 2] for i in range(0, len(newtime), 2)]
            times = datetime.datetime(int(date[0]),int(date[1]),int(date[2]), int(timeArr[0]),int(timeArr[1]))
            times = time.mktime(times.timetuple())
            # time = {"start": item["start_time"], "date": item["start_date"]}
            if times > unix_now:
                upcomings.append([streamer_name, subject, times])
    sorted_upcoming = sorted(upcomings,key=lambda x:(x[2]))[:3]
    if not init and sorted_upcoming and sorted_upcoming[0][2] - unix_now < 10 * 60:
        __main__.firebase.send_notification(sorted_upcoming[0][0])
    return sorted_upcoming


def extract_song_name(res):
    """
    Extracts the song name (artist - title) from the API response data.
    Args:
        res (object): The response data from the API call.
    Returns:
        str: Formatted string representing the song name (artist - title).
    """
    return json.loads(res.text)[0]["now_playing"]["song"]["text"]


def extrat_song_title(res):
    """
    Extracts the song title from the API response data.
    Args:
        res (object): The response data from the API call.
    Returns:
        str: Formatted string representing the song title.
    """
    return json.loads(res.text)[0]["now_playing"]["song"]["title"]


def extract_live_status(res):
    """
    Extracts the live status (True/False) from the API response data.
    Args:
        res (object): The response data from the API call.
    Returns:
        bool: True if live, False otherwise.
    """
    return json.loads(res.text)[0]["live"]["is_live"]


def extract_time(res):
    """
    Extracts the current time the song was played and converts it to datetime.
    Args:
        res (object): The response data from the API call.
    Returns:
        datetime.datetime: Object representing the time the song was played.
    """
    return datetime.datetime.fromtimestamp(json.loads(res.text)[0]["now_playing"]["played_at"])


def compare_by_time(x, y):
    return x.time < y.time  # Return True if x.time is earlier than y.time

def load_rss_feed(url:str):

    """
    Parses an RSS feed at the given URL and returns a dictionary
    containing episode dates.
    """
    # Fetch the XML data
    response = requests.get(url)
    response.raise_for_status()  # Raise exception for non-200 status codes

    # Parse the XML content
    root = ET.fromstring(response.content)
    ns = {"itunes": 'http://www.itunes.com/dtds/podcast-1.0.dtd'}

    # Define podcast dict
    podcast = {}
    podcast_req_fields = ["title", "description", "link", "itunes:image"]
    # Extract episode dates
    channel_element = root.find('channel')
    if channel_element is not None:
        for child in channel_element:
            if child.tag not in podcast_req_fields:
                continue
            if child.tag == "link":
                podcast["hostURL"] = child.text
            else:
                podcast[child.tag] = child.text  # Convert tag to lowercase, get text content

        podcast['image'] = channel_element.find('image').find('url').text
        # Process items into separate dictionaries
        episodes = []
        episodes_req_fields = ["title", "description", "pubDate", "enclosure"]
        for item in channel_element.findall('item'):
            episode = {}

            for child in item:
                if child.tag not in episodes_req_fields and not str(child.tag).__contains__("image") and not str(child.tag).__contains__("duration"):
                    continue
                if str(child.tag).__contains__("image"):
                    episode["image"] = child.get("href")
                if str(child.tag).__contains__("duration"):
                    episode['duration'] = child.text
                elif child.tag == "enclosure":
                    episode['url'] = child.get('url')
                else:
                    episode[child.tag] = child.text  # Convert tag to lowercase, get text content

            episodes.append(episode)
        podcast['episodeList'] = episodes  # Rename 'item' and store episode dictionaries

    return podcast

def read_rss_links(path:str):
  """
  Reads a list of RSS feed URLs from the given text file.
  """
  links = []
  with open(path, 'r') as f:
    for line in f:
      links.append(line.strip())  # Remove leading/trailing whitespace
  return links