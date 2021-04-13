import requests
import yaml
import json
from feedlib import Feed

config = yaml.safe_load(open("config.yaml"))


class JSONFeed(Feed):
    def __init__(self, name, description, url, text):
        Feed.__init__(self, name, description)
        self.url = url
        self.text = text

    def fetch_worksheets(self):
        res = requests.get(self.url)
        if res.status_code != 200:
            raise RuntimeError("Error accessing JSON feed")
        
        items = json.loads(res.text)
        sheets = []
        for item in items:
            sheets.append((item["title"], item["url"]))
        return sheets

    def get_updates(self):
        updates = []
        for name, link in self.fetch_worksheets():
            if not self.already_sent(link):
                updates.append(self.text.format(name=name, link=link))
                self.register_as_sent(link)
        return updates
