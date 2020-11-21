import re
import json
import requests
import datetime
import yaml
from rocketchat.api import RocketChatAPI
from feedlib import Feed

# room: "Z8dkiYCN7ky6fxqfM"

config = yaml.safe_load(open("config.yaml"))


class RocketchatYoutubeFeed(Feed):
    def __init__(self, name, description, text, rocketchat_url, rocketchat_room, youtube_channel):
        Feed.__init__(self, name, description)
        self.text = text
        self.rocketchat_url = rocketchat_url
        self.rocketchat_room = rocketchat_room
        self.youtube_channel = youtube_channel

    def check_for_links(self):
        api = RocketChatAPI(settings={
            "username": config["rocketchat_user"], "password": config["rocketchat_password"],
            "domain": self.rocketchat_url
        })

        links = []
        oldest = (datetime.datetime.now()-datetime.timedelta(seconds=86400*10)).isoformat()
        res = api.get_private_room_history(self.rocketchat_room, oldest=oldest)
        for msg in res["messages"]:
            match = re.search("https:\/\/(www\.)?youtu(be\.(com|de)|\.be)\/(watch\?v\=)?([0-9A-Za-z\-_]+)", msg["msg"])
            if match:
                yt_id = match[5]
                res = requests.get("https://youtube.googleapis.com/youtube/v3/videos",
                                   {"key": config["youtube_api_key"], "part": "snippet",
                                    "id": yt_id})
                data = json.loads(res.text)
                if data["items"][0]["snippet"]["channelId"] == self.youtube_channel:
                    links.append(match[0])
        return links

    def get_updates(self):
        updates = []
        for link in self.check_for_links():
            if not self.already_sent(link):
                updates.append(self.text.format(link=link))
                self.register_as_sent(link)
        return updates



