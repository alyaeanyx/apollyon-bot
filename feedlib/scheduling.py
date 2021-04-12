import datetime
import dateutil.parser
import csv
from feedlib import Feed


class ScheduledItem:
    def __init__(self, time, number, text):
        self.time = time
        self.number = number
        self.text = text

    def __eq__(self, other):
        return self.time == other.time and self.number == other.number and self.text == other.text

    def __ne__(self, other):
        return not self.__eq__(other)


class ScheduledFeed(Feed):
    def __init__(self, name, description, filename, text="#%d: %s"):
        Feed.__init__(self, name, description)
        self.text = text
        self.schedule = []
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.schedule.append(ScheduledItem(dateutil.parser.isoparse(row[1]), int(row[0]), row[2]))

    def get_updates(self):
        updates = []
        now = datetime.datetime.now()
        for item in self.schedule:
            if now >= item.time and not self.already_sent(item):
                updates.append(self.text.format(n=item.number, video_id=item.text))
                self.register_as_sent(item)
        return updates


class RepeatedFeed(Feed):
    def __init__(self, name, description, text, tod):
        Feed.__init__(self, name, description)
        self.text = text
        self.tod = tod

    def get_updates(self):
        if datetime.datetime.now().time() > self.tod and not self.already_sent(datetime.date.today()):
            self.register_as_sent(datetime.date.today())
            return [self.text]
        else:
            return []
