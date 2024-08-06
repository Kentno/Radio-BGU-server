import json
import time
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET

import requests

from dataclasses import dataclass

from bs4 import BeautifulSoup

import re

# Define character ranges for Arabic and Hebrew
arabic_pattern = re.compile('[\u0627-\u064a]')
hebrew_pattern = re.compile('[\u0590-\u05FF]')


def guesstextorientation(text):
    # Count occurrences of Arabic and Hebrew characters
    arabic_count = len(re.findall(arabic_pattern, text))
    hebrew_count = len(re.findall(hebrew_pattern, text))

    # Determine text orientation based on character counts
    if arabic_count > (len(text) / 2):
        return 'rtl'  # Right-to-left for Arabic
    elif hebrew_count > (len(text) / 2):
        return 'rtl'  # Right-to-left for Hebrew
    else:
        return 'ltr'  # Left-to-right for English or other languages

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


def extract_upcoming(data, firebase_obj, init=False):
    #TODO fix edge cases
    """
    return the 3 soonest broadcasts
    """
    upcomings = []
    now = datetime.now()
    unix_now = now.timestamp()
    print("extracting upcoming broadcasts " + str(init))
    for streamer in data:
        print(streamer)
        if len(streamer["schedule_items"]) == 0:
            continue
        streamer_name = streamer["display_name"]
        subject = streamer["comments"]
        for item in streamer["schedule_items"]:
            item_datetime = datetime.strptime(item["start_date"], "%Y-%m-%d")
            time_str = str(item["start_time"])
            time_str = "0" + time_str if len(time_str) == 3 else time_str
            item_datetime = item_datetime.replace(hour=int(time_str[0:2]), minute=int(time_str[2:]))
            print(item_datetime.timestamp())
            if item_datetime > now:
                upcomings.append([streamer_name, subject, item_datetime.timestamp()])
    sorted_upcoming = sorted(upcomings, key=lambda x: (x[2]))[:3]
    if not init and sorted_upcoming and sorted_upcoming[0][2] - unix_now < 10 * 60 and sorted_upcoming[0][
        2] - unix_now > 5 * 60:
        firebase_obj.send_notification(sorted_upcoming[0])
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


def load_rss_feed(url: str):
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
            elif child.tag in ["title", "description"]:
                text = html_to_string(child.text)
                podcast[child.tag] = text
                podcast[str(child.tag)+"_direction"] = guesstextorientation(text)
            else:
                podcast[child.tag] = child.text  # Convert tag to lowercase, get text content

        podcast['image'] = channel_element.find('image').find('url').text
        # Process items into separate dictionaries
        episodes = []
        episodes_req_fields = ["title", "description", "pubDate", "enclosure"]
        for item in channel_element.findall('item'):
            episode = {}

            for child in item:
                if child.tag not in episodes_req_fields and not str(child.tag).__contains__("image") and not str(
                        child.tag).__contains__("duration"):
                    continue
                if str(child.tag).__contains__("image"):
                    episode["image"] = child.get("href")
                if str(child.tag).__contains__("duration"):
                    episode['duration'] = child.text
                elif child.tag == "enclosure":
                    episode['url'] = child.get('url')
                elif child.tag in ["title", "description"]:
                    text = html_to_string(child.text)
                    episode[child.tag] = text
                    episode[str(child.tag) + "_direction"] = guesstextorientation(text)
                else:
                    episode[child.tag] = html_to_string(child.text) if child.text else ""  # Convert tag to lowercase, get text content

            episodes.append(episode)
        podcast['episodeList'] = episodes  # Rename 'item' and store episode dictionaries

    return podcast


def read_rss_links(path: str):
    """
    Reads a list of RSS feed URLs from the given text file.
    """
    links = []
    with open(path, 'r') as f:
        for line in f:
            links.append(line.strip())  # Remove leading/trailing whitespace
    return list(set(links))


def html_to_string(html_text):
    """
    Extracts text content from a string containing HTML tags.

    Args:
      html_text: String containing HTML content.

    Returns:
      String containing only the text content from the HTML.
    """
    return BeautifulSoup(html_text, "html.parser").get_text()


