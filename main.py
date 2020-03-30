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
    # layout_content = ObjectProperty(None) is it necessary??

    def __init__(self, **kwargs):
        super(HomeWindow, self).__init__(**kwargs)
        self.grid.bind(minimum_height=self.grid.setter('height'))

    current = ""

    def log_out(self):
        sm.current = "login"

    def on_enter(self, *args):
        for name, desc, auth, size in [x for x in db_f.sets for _ in range(13)]:
            button = Button(text=name + ': ' + ' by ' + auth + ' (' + size + ' flashcards)')
            button.size_hint = (0.8, 0.35)
            button.bind(on_press=self.pressed)
            self.ids.grid.add_widget(button)

    def pressed(self, instance):
        filename = instance.text.split(':')[0]
        sm.transition.direction = 'left'
        sm.current = 'learning'
        sm.current_screen.ids.set_name.text = filename + '.txt'


class LearningWindow(Screen):

    def __init__(self, **kwargs):
        super(LearningWindow, self).__init__(**kwargs)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.filename = ""

    def set_file(self, filename):
        self.filename = filename

    def browse_sets(self):
        sm.current = "home"

    def on_enter(self, *args):
        filename = self.ids.set_name.text
        flashcards = db_f.retrieve_set(filename)
        print(flashcards)
        for term, definition in flashcards:
            label_term = Label(text=term)
            label_term.canvas
            # label_term.size_hint(0.5, 0.25)
            label_def = Label(text=definition)
            # label_def.size_hint(0.5, 0.25)
            self.ids.grid.add_widget(label_term)
            self.ids.grid.add_widget(label_def)

    def pressed(self, instance):
        filename = instance.text.split(':')[0]
        instance.text = 'Opening ' + filename + '.txt'


screens = [LoginWindow(name="login"), CreateAccountWindow(name="create"),
           HomeWindow(name="home"), LearningWindow(name="learning")]

for screen in screens:
    sm.add_widget(screen)

sm.current = "home"


class MyMainApp(App):
    font_size_large = NumericProperty(20)

    def build(self):
        return sm


if __name__ == "__main__":
    MyMainApp().run()
