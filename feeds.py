import datetime
import feedlib
import feedlib.scheduling
import feedlib.rocketchat_lib
import feedlib.mampf
import feedlib.ph_uebungsgruppen
import feedlib.moodle
import feedlib.json_feed


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
        "PTP2_lectures", "Vorlesungen Theoretische Physik 2 (vorab verteile Linkliste)", "data/ptp_links.csv",
        """Vorlesung Nr. {n}:
        https://invidious.xyz/watch?v={video_id}
        https://youtube.com/watch?v={video_id}"""
    ),

    feedlib.rocketchat_lib.RocketchatYoutubeFeed(
        "PEP2_lectures", "Vorlesungen Experimentalphysik 2 (Links aus RocketChat)",
        """Neue Vorlesung:
        https://invidious.xyz/watch?v={video_id}
        https://youtube.com/watch?v={video_id}""",
        "https://uebungen.physik.uni-heidelberg.de/chat", "YdwY2wNALqNBG9sLM",
        "UCW5F1NI96JIaLbYT6f7BpdQ"
    ),

    feedlib.mampf.MampfFeed(
        "Ana2_lectures", "Vorlesungen Analysis 2 (MaMpf)",
        "Auf MaMpf wurde soeben eine neue Vorlesung für Ana hochgeladen: **{title}**\nLink: {url}",
        82, "kaviar"
    ),

    feedlib.mampf.MampfFeed(
        "LA2_lectures", "Vorlesungen Lineare Algebra 2 (MaMpf)",
        "Auf MaMpf wurde soeben eine neue Vorlesung für LA hochgeladen: **{title}**\nLink: {url}",
        86, "kaviar"
    ),

    feedlib.ph_uebungsgruppen.PHUebungsgruppenFeed(
        "PTP2_worksheets", "Übungsblätter für Theoretische Physik 2 (Übungsgruppenverwaltungssystem)",
        "Im Übungsgruppenverwaltungssystem wurde soeben das Übungsblatt **{name}** hochgeladen:\n{link}",
        1290
    ),

    feedlib.moodle.MoodleTypeAFeed(
        "PEP2_worksheets", "Übungsblätter für Experimentalphysik 2 (Moodle)",
        "Im Moodle wurde soeben das Übungsblatt **{name}** hochgeladen:\n{link}",
        7061
    ),

    feedlib.mampf.MampfFeed(
        "Ana2_worksheets", "Übungsblätter für Analysis 2 (MaMpf)",
        "Auf MaMpf wurde soeben eine neue Datei für Ana hochgeladen: **{title}**\nLink: {url}",
        82, "nuesse"
    ),

    feedlib.mampf.MampfFeed(
        "LA2_worksheets", "Übungsblätter für Lineare Algebra 2 (MaMpf)",
        "Auf MaMpf wurde soeben eine neue Datei für LA hochgeladen: **{title}**\nLink: {url}",
        86, "nuesse"
    ),
    
    feedlib.json_feed.JSONFeed(
    "HöMa2_files", "Dateien für HöMa2", "https://uni.ericbiedert.de/homa",
    """Neue Datei für HöMa: **{name}**
    {link}"""
    ),

    feedlib.DeveloperFeed("DevLog", "Developer message log")

    #feedlib.Feed("Ana1_lectures", "Vorlesungen Analysis 1"),
    #feedlib.Feed("LA1_lectures", "Vorlesungen Lineare Algebra 1")
]
