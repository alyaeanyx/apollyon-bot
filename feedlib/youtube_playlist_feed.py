import re
import json
import requests
import datetime
import yaml
from rocketchat.api import RocketChatAPI
from feedlib import Feed


config = yaml.safe_load(open("config.yaml"))


class YoutubePlaylistFeed(Feed):
    def __init__(self, name, description, text, youtube_playlist):
        Feed.__init__(self, name, description)
        self.text = text
        self.youtube_playlist = youtube_playlist
        
    def check_for_links(self):
        res = requests.get("https://youtube.googleapis.com/youtube/v3/playlistItems",
                               {"key": config["youtube_api_key"], "part": "id,contentDetails",
                               "playlistId": self.youtube_playlist})
        data = json.loads(res.text)
        links = []
        for item in data["items"]:
            links.append(item["contentDetails"]["videoId"])
        return links

    def get_updates(self):
        updates = []
        for link in self.check_for_links():
            if not self.already_sent(link):
                updates.append(self.text.format(video_id=link))
                self.register_as_sent(link)
        return updates
