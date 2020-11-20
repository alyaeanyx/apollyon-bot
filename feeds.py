import datetime
import feedlib
import feedlib.scheduling


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
        "PTP1_lectures", "Vorlesungen Theoretische Physik 1", "data/ptp_links.csv",
        """Vorlesung Nr. %d:\n%s"""
    ),

    feedlib.scheduling.RepeatedFeed(
        "WPAstro1_lectures_reminder", "Erinnerungen an Astronomie-1-Vorlesung",
        "Erinnerung an die Astronomie-Vorlesung um 14:15!", datetime.time(21, 19, 00)
    ),

    feedlib.Feed("Ana1_lectures", "Vorlesungen Analysis 1"),
    feedlib.Feed("LA1_lectures", "Vorlesungen Lineare Algebra 1")
]

