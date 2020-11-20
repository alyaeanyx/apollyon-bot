import pickle


class Feed:
    def __init__(self, name, description):
        self.name = name
        self.description = description

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

