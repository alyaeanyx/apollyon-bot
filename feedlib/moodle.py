import requests
import yaml
from bs4 import BeautifulSoup
from feedlib import Feed
import re

config = yaml.safe_load(open("config.yaml"))


def login():
    res1 = requests.get("https://moodle.uni-heidelberg.de/login/index.php")
    if res1.status_code == 503:
        return ""
    doc1 = BeautifulSoup(res1.text, "html.parser")
    logintoken = doc1.find("input", attrs={"name": "logintoken"})["value"]
    session_id = res1.cookies.get("MoodleSession")

    res2 = requests.post("https://moodle.uni-heidelberg.de/login/index.php",
                         data={"anchor": "",
                               "logintoken": logintoken,
                               "username": config["moodle_user"],
                               "password": config["moodle_password"]
                               },
                         cookies={
                             "MoodleSession": session_id
                         },
                         allow_redirects=False
                         )
    return res2.cookies.get("MoodleSession")


""""
The Moodle interface seems to have no common standard at all for formatting links on the course pages.
Feel free to write your own subclass for new courses. And congratulations to whoever the hell designed this system.
At least they used HTML.
"""

class MoodleFeed(Feed):
    def __init__(self, name, description, text, course_id):
        Feed.__init__(self, name, description)
        self.session_id = login()
        self.text = text
        self.course_id = course_id

    def request_ensure_login(self, url):
        try:
            res = requests.get(url, cookies={"MoodleSession": self.session_id}, allow_redirects=False)
        except requests.exceptions.ConnectionError:
            self.session_id = login()
            res = requests.get(url, cookies={"MoodleSession": self.session_id}, allow_redirects=False)

        if res.status_code == 503:
            return None

        if res.status_code != 200:
            #if res.status_code == 303:
            self.session_id = login()
            res = requests.get(url, cookies={"MoodleSession": self.session_id}, allow_redirects=False)
            if res.status_code != 200:
                raise RuntimeError("Moodle login failed")
            #else:
            #    raise RuntimeError("Failed to access Moodle")
        return res

    def get_updates(self):
        updates = []
        for name, link in self.fetch_worksheets():
            if not self.already_sent(link):
                updates.append(self.text.format(name=name, link=link))
                self.register_as_sent(link)
        return updates


class MoodleTypeAFeed(MoodleFeed):
    """
    Tested for course PEP1 WS20
    """
    def __init__(self, name, description, text, course_id):
        MoodleFeed.__init__(self, name, description, text, course_id)

    def fetch_worksheets(self):
        url = f"https://moodle.uni-heidelberg.de/course/view.php?id={self.course_id}"
        res = self.request_ensure_login(url)
        if res is None:
            return []
        doc = BeautifulSoup(res.text, "html.parser")
        links = []
        for a in doc.find_all("a", attrs={"class": "aalink"}):
            match = re.search("(Übungsblatt [0-9]+) Datei", a.span.text)
            if match:
                links.append((match[1], a["href"]))
        return links


class MoodleTypeBFeed(MoodleFeed):
    """
    Tested for course Astro I
    Seriously, it seems like we'll need one class for every single course.
    May the days of the person who devised this website be short and let another take their office.
    May they be cast into the bowels of the earth and suffer eternal torture for their crimes.
    May they realize what they did by themself.
    """
    def __init__(self, name, description, text, course_id):
        MoodleFeed.__init__(self, name, description, text, course_id)

    def fetch_worksheets(self):
        url = f"https://moodle.uni-heidelberg.de/course/view.php?id={self.course_id}"
        res = self.request_ensure_login(url)
        if res is None:
            return []
        doc = BeautifulSoup(res.text, "html.parser")

        links = []
        for a in doc.find_all("a", attrs={"class": "aalink"}):
            if a["href"].startswith("https://moodle.uni-heidelberg.de/mod/assign/"):
                links.append((a.text.rstrip(" Aufgabe"), a["href"]))
        return links

