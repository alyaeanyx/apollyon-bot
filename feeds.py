import datetime
import feedlib
import feedlib.scheduling
import feedlib.rocketchat_lib
import feedlib.mampf


def get_feed(name):
    for feed in FEEDS:
        if feed.name == name:
            return feed
    raise KeyError(f"No feed called '{name}'")


def feed_exists(name):
    for feed in FEEDS:
        if feed.name == name:
            return True
    return False


FEEDS = [
    feedlib.scheduling.ScheduledFeed(
        "PTP1_lectures", "Vorlesungen Theoretische Physik 1 (vorab verteile Linkliste)", "data/ptp_links.csv",
        """Vorlesung Nr. %d:\n%s"""
    ),

    feedlib.rocketchat_lib.RocketchatYoutubeFeed(
        "PEP1_lectures", "Vorlesungen Experimentalphysik 1 (Links aus RocketChat)",
        "Auf RocketChat wurde soeben ein neuer Link für PEP1 geposted:\n{link}",
        "https://uebungen.physik.uni-heidelberg.de/chat", "Z8dkiYCN7ky6fxqfM",
        "UCW5F1NI96JIaLbYT6f7BpdQ"
    ),

    feedlib.mampf.MampfFeed(
        "Ana1_lectures", "Vorlesungen Analysis 1 (MaMpf)",
        "Auf MaMpf wurde soeben eine neue Vorlesung für Ana1 hochgeladen: **{title}**\nLink: {url}",
        43, "kaviar"
    ),

    feedlib.mampf.MampfFeed(
        "LA1_lectures", "Vorlesungen Lineare Algebra 1 (MaMpf)",
        "Auf MaMpf wurde soeben eine neue Vorlesung für LA1 hochgeladen: **{title}**\nLink: {url}",
        58, "kaviar"
    ),

    feedlib.scheduling.RepeatedFeed(
        "WPAstro1_lectures_reminder", "Erinnerungen an Astronomie-1-Vorlesung",
        "Erinnerung an die Astronomie-Vorlesung um 14:15!", datetime.time(21, 19, 00)
    ),

    feedlib.mampf.MampfFeed(
        "Ana1_worksheets", "Übungsblätter für Analysis 1 (MaMpf)",
        "Auf MaMpf wurde soeben eine neue Datei für Ana1 hochgeladen: **{title}**\nLink: {url}",
        43, "nuesse"  # do not fucking ask me why those people name their pages like this
    ),

    feedlib.mampf.MampfFeed(
        "LA1_worksheets", "Übungsblätter für Lineare Algebra 1 (MaMpf)",
        "Auf MaMpf wurde soeben eine neue Datei für LA1 hochgeladen: **{title}**\nLink: {url}",
        58, "nuesse"
    ),

    feedlib.DeveloperFeed("DevLog", "Developer message log")

    #feedlib.Feed("Ana1_lectures", "Vorlesungen Analysis 1"),
    #feedlib.Feed("LA1_lectures", "Vorlesungen Lineare Algebra 1")
]

