import requests
import yaml
from bs4 import BeautifulSoup
from feedlib import Feed

config = yaml.safe_load(open("config.yaml"))


def login():
    res = requests.post("https://uebungen.physik.uni-heidelberg.de/uebungen/login.php",
                        data={
                            "username": config["phug_user"],
                            "loginpass": config["phug_password"],
                            "submit": "+submit+"
                        }, allow_redirects=False)
    return res.cookies.get("PHPSESSID")



class PHUebungsgruppenFeed(Feed):
    def __init__(self, name, description, text, group_id):
        Feed.__init__(self, name, description)
        self.text = text
        self.group_id = group_id
        self.session_id = login()

    def fetch_worksheets(self):
        """
        So far, this function was only tested for the group "PTP1 Group F" (group_id=1207). Due to shoddy and
        inconsistent web development of the Übungsgruppenverwaltungssystem, it doesn't seem to work consistently
        with all groups, as there are different standards for the exercise link format. If you wish to add another group
        format, a pull request on GitHub would be welcome. Just add an if statement distinguishing between different
        formats.
        """
        url = f"https://uebungen.physik.uni-heidelberg.de/uebungen/mygroups.php?vid={self.group_id}"
        res = requests.get(url, cookies={"PHPSESSID": self.session_id}, allow_redirects=False)
        if res.status_code != 200:
            if res.status_code == 302:
                self.session_id = login()
                res = requests.get(url, cookies={"PHPSESSID": self.session_id}, allow_redirects=False)
                if res.status_code != 200:
                    raise RuntimeError("couldn't login to Physik Übungsgruppen system")
            else:
                raise RuntimeError("couldn't access Physik Übungsgruppen system")

        doc = BeautifulSoup(res.text, "html.parser")

        sheets = []
        for a in doc.find_all("a"):
            if not a.has_attr("href"):
                continue
            if a["href"].startswith("/uebungen/download/"):
                sheets.append((a.text, a["href"]))

        return sheets

    def get_updates(self):
        updates = []
        for name, link in self.fetch_worksheets():
            if not self.already_sent(link):
                updates.append(self.text.format(name=name, link="https://uebungen.physik.uni-heidelberg.de"+link))
                self.register_as_sent(link)
        return updates
