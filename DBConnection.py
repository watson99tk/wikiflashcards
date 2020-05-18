from datetime import datetime

import pymongo
import classes
from bson.objectid import ObjectId


class AuthenticationException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class AddValueException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class DatabaseException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class DBConnection:
    def __init__(self):
        client = pymongo.MongoClient(
            "mongodb+srv://Developer:TrustMe99@flipcardsdb-k8zdx.mongodb.net/test?retryWrites=true&w=majority")
        self.db = client["FlipcardsDB"]

    def list_users(self):
        users = self.db["users"]
        for user in users.find():
            print(user)

    def get_user(self, name):
        users = self.db["users"]
        amount = users.count_documents({"UserName": name})
        if amount == 0:
            return 0
        else:
            return users.find({"UserName": name})

    def get_set(self, set_id):
        result_cards = []
        if self.db["cardssets"].count_documents({"_id": ObjectId(set_id)}) == 0:
            raise DatabaseException("No such set")
        cards_set = self.db["cardssets"].find({"_id": ObjectId(set_id)})
        for card_id in cards_set["cards"]:
            card = self.db["flashcards"].findOne({"_id": ObjectId(card_id)})
            result_cards.append(classes.Flashcard(card["Question"], card["Answer"], card["Set"], card["User"]))
        return classes.Set(cards_set["Creator"], result_cards, cards_set["SetTime"], cards_set["StudyTime"], set_id)

    def add_user(self, user_name, user_email, user_password):
        if len(user_password) < 8:
            raise AddValueException("Too short password")
        already_exists = self.db["users"].count_documents({"UserName": user_name})
        if already_exists > 0:
            raise (DatabaseException("User already exists"))
        users = self.db["users"]
        users.insert_one({"UserName": user_name, "password": user_password, "email": user_email, "cardsCreated": 0})

    def user_auth(self, user_name, given_password):
        user = self.get_user(user_name)
        if user == 0:
            raise AuthenticationException("No such user")
        result = self.db["users"].count_documents({'UserName': user_name, 'password': given_password})
        if result == 0:
            raise AuthenticationException("Password incorrect")
        return 1

    def add_flashcard(self, question, answer, creator_id, set_id):
        flashcards = self.db["flashcards"]
        if self.db["users"].count_documents({"_id": ObjectId(creator_id)}) == 0:
            raise DatabaseException("No such user")
        query = {"Question": question, "Answer": answer, "User": creator_id, "Set": set_id}
        if self.db["flashcards"].count_documents(query) != 0:
            raise DatabaseException("You have already created such flashcard")
        flash_card_id = flashcards.insert_one(
            {"Question": question, "Answer": answer, "User": creator_id, "Set": set_id}).inserted_id
        print(flash_card_id)
        self.db["cardssets"].update_one({"_id": ObjectId(set_id)}, {"$addToSet": {"cards": flash_card_id}})

    def add_flashcard_mark(self, card_id, user_id, mark):
        if self.db["flashcards"].count_documents({"_id": ObjectId(card_id)}) == 0:
            raise DatabaseException("No such card")
        card = self.db["flashcards"].find_one({"_id": ObjectId(card_id)})
        already_exists = self.db["ratings"].count_documents({"User": user_id, "Card": card_id})
        if already_exists == 0:
            self.db["ratings"].insert_one({"User": user_id, "Card": card_id, "Date": datetime.now(), "Mark": mark})
        else:
            self.db["ratings"].update_one({"User": user_id, "Card": card_id}, {"Date": datetime.now(), "Mark": mark})
        self.update_avarege_mark(card["_id"])

    def update_avarege_mark(self, card_id):
        ratings = self.db["ratings"].find({"Card": card_id})
        marks_sum = 0
        marks_amount = 0
        for rating in ratings:
            marks_sum += rating["Mark"]
            marks_amount += 1
        self.db["flashcards"].update_one({"_id": card_id}, {"avg_mark": round(marks_sum / marks_amount, 2)})

    def get_flashcard_average_mark(self, card_id):
        return (self.db["flashcards"].find_one({"_id": card_id}))["avg_mark"]

    #TODO
    def upload_set(self, cards_set):
        if cards_set.ID == 0:
            for flashcard in cards_set.Flashcards:
                self.add_flashcard(flashcard.Question, flashcard.Answer, flashcard.User, flashcard.Set)

    def sets_list_for_selection(self, search_word):
        result_sets = []
        for cards_set in self.db["cardssets"].find():
            if search_word in cards_set["description"]:
                result_sets.append(cards_set)
        return result_sets

    #TODO
    def has_already_rated(self, user_id, card_id):
        print("todotodotodotodotooooodq")

# db = DBConnection()
# print("Users list:")
# db.list_users()
# print("User 1:")
# db.get_user("usr1")
# db.add_user("userFromPython3", "user3@email.com", "passwordVeryStrong")
# print("User from python:")
# for user in db.get_user("userFromPython"):
# print(user)
# db.add_flashcard("czy bazy2 to najlepszy przedmiotyyyyyyyyyyyyy3333", "no chyba raczej a jak",
#                 "5eb6bf2bac666a10cbe7b395",
#                 "5eb746d292763182cc3c8362")
# print(db.user_auth("userFromPython", "passwordVeryStrong"))
# print(db.user_auth("userFromPython", "veryWrongPassword"))
# db.add_flashcard_mark("5eb807df9217647fbe7ab1bb", 5)
# db.add_flashcard_mark("5eb807df9217647fbe7ab1bb", 3)
# print(db.get_flashcard_average_mark("5eb807df9217647fbe7ab1bb"))
