import pickle


class Feed:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.public = True

    def get_updates(self):
        return []

    def register_as_sent(self, item):
        try:
            sent_items = pickle.load(open("data/sent/"+self.name, "rb"))
            pfile = open("data/sent/"+self.name, "wb")
            pickle.dump(sent_items+[item], pfile)
            pfile.close()
        except (FileNotFoundError, EOFError) as e:
            pfile = open("data/sent/" + self.name, "wb")
            pickle.dump([item], pfile)
            pfile.close()

    def already_sent(self, item):
        try:
            sent_items = pickle.load(open("data/sent/" + self.name, "rb"))
            return item in sent_items
        except (FileNotFoundError, EOFError) as e:
            return False


class DeveloperFeed(Feed):
    def __init__(self, name, description):
        Feed.__init__(self, name, description)
        self.public = False
        self.updates = []

    def add_update(self, update):
        self.updates.append(update)

    def get_updates(self):
        updates = self.updates[:]
        self.updates = []
        return updates
