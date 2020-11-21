import requests
import yaml
from bs4 import BeautifulSoup
from feedlib import Feed

config = yaml.safe_load(open("config.yaml"))


def login():
    res1 = requests.get("https://mampf.mathi.uni-heidelberg.de/users/sign_in")
    doc1 = BeautifulSoup(res1.text, "html.parser")
    auth_token = doc1.find("input", attrs={"name": "authenticity_token"}).attrs["value"]

    login_data = {"authenticity_token": auth_token,
                  "user[email]": config["mampf_email"], "user[password]": config["mampf_password"],
                  "user[remember_me]": 1, "commit": "Einloggen"}
    res2 = requests.post("https://mampf.mathi.uni-heidelberg.de/users/sign_in", data=login_data, allow_redirects=False, cookies=res1.cookies)
    return res2.cookies.get("remember_user_token")


class MampfFeed(Feed):
    def __init__(self, name, description, text, lecture_id, project_id):
        Feed.__init__(self, name, description)
        self.lecture_id = lecture_id
        self.project_id = project_id
        self.text = text
        self.token = login()

    def get_updates(self):
        url = f"https://mampf.mathi.uni-heidelberg.de/lectures/{self.lecture_id}/food?project={self.project_id}"

        res = requests.get(url, cookies={"remember_user_token": self.token})
        if res.status_code != 200:
            if res.status_code == 302:
                self.token = login
                res = requests.get(url, cookies={"remember_user_token": self.token})
                if res.status_code != 200:
                    raise RuntimeError("failed to log in to MaMpf")
            else:
                raise RuntimeError("Failed to query MaMpf")

        doc = BeautifulSoup(res.text, "html.parser")
        cards = doc.find_all(id="media-card-subheader")

        titles = []
        for card in cards:
            titles.append(card.find("h5").text.strip())

        updates = []
        for title in titles:
            if not self.already_sent(title):
                updates.append(self.text.format(title=title, url=url))
                self.register_as_sent(title)
        return updates