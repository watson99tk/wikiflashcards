import datetime
from os import listdir


# from os.path import isfile, join


class UserDataBase:
    def __init__(self, filename):
        self.filename = filename
        self.users = None
        self.file = None
        self.load()

    def load(self):
        self.file = open(self.filename, "r")
        self.users = {}

        for line in self.file:
            email, password, name, created = line.strip().split(";")
            self.users[email] = (password, name, created)

        self.file.close()

    def get_user(self, email):
        if email in self.users:
            return self.users[email]
        else:
            return -1

    def add_user(self, email, password, name):
        if email.strip() not in self.users:
            self.users[email.strip()] = (password.strip(), name.strip(), UserDataBase.get_date())
            self.save()
            return 1
        else:
            print("Email exists already")
            return -1

    def validate(self, email, password):
        if self.get_user(email) != -1:
            return self.users[email][0] == password
        else:
            return False

    def save(self):
        with open(self.filename, "w") as f:
            for user in self.users:
                f.write(user + ";" + self.users[user][0] + ";" + self.users[user][1] + ";" + self.users[user][2] + "\n")

    @staticmethod
    def get_date():
        return str(datetime.datetime.now()).split(" ")[0]


class FlashCardDatabase:
    def __init__(self):
        self.sets = self._get_sets()

    def _get_sets(self):
        set_names = [f for f in listdir('sets')]
        sets = []
        for filename in set_names:
            desc, author, size = self._get_header(filename)
            sets.append((filename.split('.')[0], desc, author, size))
        return sets

    def _get_header(self, filename):
        with open('sets/' + filename, 'r') as file:
            line = file.readline().strip()
            return line.split(',')

    def retrieve_set(self, filename):
        cards_set = []
        with open('sets/' + filename, 'r') as file:
            next(file)
            for line in file:
                cards_set.append(line.strip().split(','))
        return cards_set
