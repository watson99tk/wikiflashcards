from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from database import UserDataBase, FlashCardDatabase


kv = Builder.load_file("my.kv")


class WindowManager(ScreenManager):
    pass


sm = WindowManager()
db_u = UserDataBase("users.txt")
db_f = FlashCardDatabase()


class CreateAccountWindow(Screen):
    namee = ObjectProperty(None)
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    font_size_large = NumericProperty(20)

    def submit(self):
        if self.namee.text != "" and self.email.text != "" and self.email.text.count("@") == 1 and self.email.text.count(".") > 0:
            if self.password != "":
                db_u.add_user(self.email.text, self.password.text, self.namee.text)

                self.reset()

                sm.current = "login"

    def login(self):
        self.reset()
        sm.current = "login"

    def reset(self):
        self.email.text = ""
        self.password.text = ""
        self.namee.text = ""


class LoginWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    def loginBtn(self):
        if db_u.validate(self.email.text, self.password.text):
            HomeWindow.current = self.email.text
            self.reset()
            sm.current = "home"

    def createBtn(self):
        self.reset()
        sm.current = "create"

    def reset(self):
        self.email.text = ""
        self.password.text = ""


class HomeWindow(Screen):
    current = ""

    def logOut(self):
        sm.current = "login"

    def on_enter(self, *args):
        print(db_f.sets)
        for name, desc, auth, size in [x for x in db_f.sets for _ in range(3)]:
            button = Button(text=name + ': ' + ' by ' + auth + ' (' + size + ' flashcards)')
            button.size_hint = (0.8, 0.35)
            button.on_press()
            self.ids.grid.add_widget(button)


screens = [LoginWindow(name="login"), CreateAccountWindow(name="create"), HomeWindow(name="home")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "home"


class MyMainApp(App):
    font_size_large = NumericProperty(20)

    def build(self):
        return sm


if __name__ == "__main__":
    MyMainApp().run()
