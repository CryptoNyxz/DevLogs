"""
Frontend Implementation.

Where the front end is implemented.
"""
from threading import Thread
from time import sleep
from typing import Optional
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from backend import Account, Entry, SessionManager
from exceptions import AccountExists, AccountNotFound
from exceptions import InvalidAccountFormat, InvalidCredentials
from exceptions import TooManyAttempts
from globaldata import __author__, __version__, __license__
from utils import timestamp


__author__ = __author__
__version__ = __version__
__license__ = __license__


orientation = 0


if orientation == 0:  # Horizontal
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '560')
elif orientation == 1:  # Vertical
    Config.set('graphics', 'width', '560')
    Config.set('graphics', 'height', '400')
Config.set('graphics', 'resizable', False)


class FrontWindow(BoxLayout):
    """
    Front Display Window.
    This window is shown before logging in or signing up.
    :param app: The Kivy App instance that will use this window.
    """

    def __init__(self, app, **kwargs):
        super(FrontWindow, self).__init__(**kwargs)

        self.app = app

        self.ids['switch_login'].on_press = self.switch_login
        self.ids['switch_signup'].on_press = self.switch_signup

    def switch_login(self):
        """Switch to login window."""
        self.app._current_window.clear_widgets()
        self.app._current_window.add_widget(self.app._login_window)

    def switch_signup(self):
        """Switch to Sign Up window."""
        self.app._current_window.clear_widgets()
        self.app._current_window.add_widget(self.app._signup_window)


Builder.load_string('''
<FrontWindow>:
    orientation: "vertical"

    Widget:
        size_hint: (1, .2)

    Image:
        source: "../images/icon.png"
        size_hint: (1, .325)

    Label:
        text: "DevLogs"
        font_name: "../fonts/jd_led7.ttf"
        font_size: 40
        valign: "middle"
        size_hint: (1, .195)

    Widget:
        size_hint: (1, .005)

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .075)

        Widget:
            size_hint: (.25, 1)

        Button:
            id: switch_login
            text: "Login"
            font_name: "../fonts/jd_led7.ttf"
            background_color: .15, .15, .15, 1
            size_hint: (.2, 1)

        Widget:
            size_hint: (.1, 1)

        Button:
            id: switch_signup
            text: "Sign Up"
            font_name: "../fonts/jd_led7.ttf"
            background_color: .15, .15, .15, 1
            size_hint: (.2, 1)

        Widget:
            size_hint: (.25, 1)

    Widget:
        size_hint: (1, .2)
''')


class LoginWindow(BoxLayout):
    """
    Login Window.
    This window is show when the user is about to log in.
    :param app: The Kivy App instance that will use this window.
    """

    def __init__(self, app, **kwargs):
        super(LoginWindow, self).__init__(**kwargs)

        self.app = app

        self.ids['login_button'].on_press = self.try_login
        self.ids['back_button'].on_press = self.switch_home

    def set_system_message(self, message: str, life: Optional[int] = None):
        """
        Set the system message.
        :param message: The system message to be shown.
        :param life: If set to None, show message indefinitely until
        replaced, if not show for a limited amount of time.
        """
        self.ids['system_message'].text = message

        def wait(life):
            if life:
                sleep(life)
                self.ids['system_message'].text = ''

        Thread(target=wait, args=(life,)).start()

    def try_login(self):
        """Attempt to Log in."""
        username = self.ids['username'].text
        password = self.ids['password'].text

        try:
            self.app.session_manager.create_session(username, password)

            self.set_system_message('[color=#00ff00]'
                                    'Success![/color]')

            Clock.schedule_once(self.switch_dashboard, 1)
        except AccountNotFound:
            self.set_system_message('[color=#ff0000]'
                                    'Account doesn\'t exist[/color]', 3)
        except InvalidCredentials:
            self.set_system_message('[color=#ff0000]'
                                    'Password is incorrect[/color]', 3)
        except InvalidAccountFormat:
            self.set_system_message('[color=#ff0000]Account is [n]probably[/b]'
                                    ' corrupted [b]OR[/b] \npassword is '
                                    'incorrect[/color]', 3)
        except TooManyAttempts:
            self.set_system_message('[color=#ff0000]Too many failed attempts'
                                    '[/color]', 3)

    def clear_window(self):
        """Clear window."""
        self.ids['system_message'].text = ''
        self.ids['username'].text = ''
        self.ids['password'].text = ''

    def switch_home(self):
        """Switch to home page."""
        self.clear_window()
        self.app._current_window.clear_widgets()
        self.app._current_window.add_widget(self.app._front_window)

    def switch_dashboard(self, instance):
        """Switch to dashboard."""
        self.clear_window()
        self.app._current_window.clear_widgets()
        self.app._dashboard_window.prepare_dashboard()
        self.app._current_window.add_widget(self.app._dashboard_window)


Builder.load_string('''
<LoginWindow>:
    orientation: "vertical"

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .075)

        Button:
            id: back_button
            text: "<"
            font_name: "../fonts/modernpics.otf"
            font_size: 30
            background_color: 0, 0, 0, 0
            size_hint: (.175, 1)

        Widget:
            size_hint: (.825, 1)

    Widget:
        size_hint: (1, .05)

    Image:
        source: "../images/icon.png"
        size_hint: (1, .225)

    Label:
        text: "DevLogs"
        font_name: "../fonts/jd_led7.ttf"
        font_size: 40
        halign: "center"
        valign: "middle"
        size_hint: (1, .12)

    Label:
        text: "Login"
        font_name: "../fonts/jd_led7.ttf"
        font_size: 20
        text_size: self.size
        halign: "center"
        valign: "middle"
        size_hint: (1, .075)

    Label:
        id: system_message
        font_name: "../fonts/jd_led7.ttf"
        text_size: self.size
        halign: "center"
        valign: "middle"
        multiline: True
        markup: True
        size_hint: (1, .1)

    Widget:
        size_hint: (1, .005)

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .075)

        Widget:
            size_hint: (.075, 1)

        Label:
            text: "Username"
            font_name: "../fonts/jd_led7.ttf"
            text_size: self.size
            halign: "left"
            valign: "middle"
            size_hint: (.275, 1)

        Widget:
            size_hint: (.05, 1)

        TextInput:
            id: username
            hint_text: "Enter username here"
            font_name: "../fonts/jd_led7.ttf"
            text_size: self.size
            halign: "left"
            valign: "middle"
            write_tab: False
            multiline: False
            size_hint: (.525, 1)

        Widget:
            size_hint: (.075, 1)

    Widget:
        size_hint: (1, .025)

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .075)

        Widget:
            size_hint: (.075, 1)

        Label:
            text: "Password"
            font_name: "../fonts/jd_led7.ttf"
            text_size: self.size
            halign: "left"
            valign: "middle"
            size_hint: (.275, 1)

        Widget:
            size_hint: (.05, 1)

        TextInput:
            id: password
            hint_text: "Enter password here"
            font_name: "../fonts/jd_led7.ttf"
            text_size: self.size
            halign: "left"
            valign: "middle"
            password: True
            write_tab: False
            multiline: False
            size_hint: (.525, 1)

        Widget:
            size_hint: (.075, 1)

    Widget:
        size_hint: (1, .050)

    BoxLayout:
        size_hint: (1, .075)

        Widget:
            size_hint: (.4, 1)

        Button:
            id: login_button
            text: "Login"
            font_name: "../fonts/jd_led7.ttf"
            text_size: self.size
            halign: "center"
            valign: "middle"
            background_color: .15, .15, .15, 1
            size_hint: (.2, 1)

        Widget:
            size_hint: (.4, 1)

    Widget:
        size_hint: (1, .05)
''')


class SignUpWindow(BoxLayout):
    """
    Sign up Window.
    This window is shown when the user is about to sign up.
    :param app: The Kivy App instance that will use this window.
    """

    def __init__(self, app, **kwargs):
        super(SignUpWindow, self).__init__(**kwargs)

        self.app = app

        self.ids['signup_button'].on_press = self.try_signup
        self.ids['back_button'].on_press = self.switch_home

    def set_system_message(self, message: str, life: Optional[int] = None):
        """
        Set the system message.
        :param message: The system message to be shown.
        :param life: If set to None, show message indefinitely until
        replaced, if not show for a limited amount of time.
        """
        self.ids['system_message'].text = message

        def wait(life):
            if life:
                sleep(life)
                self.ids['system_message'].text = ''

        Thread(target=wait, args=(life,)).start()

    def try_signup(self):
        """Attempt to sign up."""
        username = self.ids['username'].text
        password = self.ids['password'].text

        try:
            Account.create_account(username, password)
            self.app.session_manager.create_session(username, password)

            self.set_system_message('[color=#00ff00]'
                                    'Success![/color]')

            Clock.schedule_once(self.switch_dashboard, 1)
        except AccountExists:
            self.set_system_message('[color=#ff0000]'
                                    'Account exists![/color]', 3)
        except AccountNotFound:
            self.set_system_message('[color=#ff0000]'
                                    'Failed to create account[/color]', 3)

    def clear_window(self):
        """Clear window."""
        self.ids['system_message'].text = ''
        self.ids['username'].text = ''
        self.ids['password'].text = ''

    def switch_home(self):
        """Switch to home page."""
        self.clear_window()
        self.app._current_window.clear_widgets()
        self.app._current_window.add_widget(self.app._front_window)

    def switch_dashboard(self, instance):
        """Switch to dashboard."""
        self.clear_window()
        self.app._current_window.clear_widgets()
        self.app._dashboard_window.prepare_dashboard()
        self.app._current_window.add_widget(self.app._dashboard_window)


Builder.load_string('''
<SignupWindow>:
    orientation: "vertical"

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .075)

        Button:
            id: back_button
            text: "<"
            font_name: "../fonts/modernpics.otf"
            font_size: 30
            background_color: 0, 0, 0, 0
            size_hint: (.175, 1)

        Widget:
            size_hint: (.825, 1)

    Widget:
        size_hint: (1, .05)

    Image:
        source: "../images/icon.png"
        size_hint: (1, .225)

    Label:
        text: "DevLogs"
        font_name: "../fonts/jd_led7.ttf"
        font_size: 40
        text_size: self.size
        halign: "center"
        valign: "middle"
        size_hint: (1, .12)

    Label:
        text: "Sign Up"
        font_name: "../fonts/jd_led7.ttf"
        font_size: 20
        text_size: self.size
        halign: "center"
        valign: "middle"
        size_hint: (1, .075)

    Label:
        id: system_message
        font_name: "../fonts/jd_led7.ttf"
        text_size: self.size
        halign: "center"
        valign: "middle"
        multiline: True
        markup: True
        size_hint: (1, .1)

    Widget:
        size_hint: (1, .005)

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .075)

        Widget:
            size_hint: (.075, 1)

        Label:
            text: "Username"
            font_name: "../fonts/jd_led7.ttf"
            text_size: self.size
            halign: "left"
            valign: "middle"
            size_hint: (.275, 1)

        Widget:
            size_hint: (.05, 1)

        TextInput:
            id: username
            hint_text: "Enter username here"
            font_name: "../fonts/jd_led7.ttf"
            text_size: self.size
            halign: "left"
            valign: "middle"
            write_tab: False
            multiline: False
            size_hint: (.525, 1)

        Widget:
            size_hint: (.075, 1)

    Widget:
        size_hint: (1, .025)

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .075)

        Widget:
            size_hint: (.075, 1)

        Label:
            text: "Password"
            font_name: "../fonts/jd_led7.ttf"
            text_size: self.size
            halign: "left"
            valign: "middle"
            size_hint: (.275, 1)

        Widget:
            size_hint: (.05, 1)

        TextInput:
            id: password
            hint_text: "Enter password here"
            font_name: "../fonts/jd_led7.ttf"
            text_size: self.size
            halign: "left"
            valign: "middle"
            password: True
            write_tab: False
            multiline: False
            size_hint: (.525, 1)

        Widget:
            size_hint: (.075, 1)

    Widget:
        size_hint: (1, .05)

    BoxLayout:
        size_hint: (1, .075)

        Widget:
            size_hint: (.4, 1)

        Button:
            id: signup_button
            text: "Sign Up"
            font_name: "../fonts/jd_led7.ttf"
            text_size: self.size
            halign: "center"
            valign: "middle"
            background_color: .15, .15, .15, 1
            size_hint: (.2, 1)

        Widget:
            size_hint: (.4, 1)

    Widget:
        size_hint: (1, .05)
''')


class DashboardEntry(BoxLayout):
    """
    A Dashboard Entry.
    :param entry: The Entry instance to create a GUI representation of.
    """

    def __init__(self, entry: Entry, app, **kwargs):
        super(DashboardEntry, self).__init__(**kwargs)

        self.entry = entry
        self.app = app

        self.ids['timestamp'].text = timestamp(self.entry.time_created * 1e-9)
        self.ids['entry_title'].text = self.entry.title

        self.ids['edit_button'].on_press = self.switch_edit
        self.ids['delete_button'].on_press = self.delete
        self.ids['move_up_button'].on_press = self.move_up
        self.ids['move_down_button'].on_press = self.move_down

    def switch_edit(self):
        """Switch to logedit window."""
        self.app._logedit_window.set_entry(self.entry)
        self.app._current_window.clear_widgets()
        self.app._current_window.add_widget(self.app._logedit_window)

    def delete(self):
        """Delete entry."""
        self.app.session_manager.current_session.account.\
            del_entry(self.entry)
        self.app.session_manager.save_account()
        self.app._dashboard_window.prepare_dashboard()

    def move_up(self):
        """Move entry up in entry order."""
        self.app.session_manager.current_session.account.\
            move_entry_up(self.entry)
        self.app.session_manager.save_account()
        self.app._dashboard_window.prepare_dashboard()

    def move_down(self):
        """Move entry down in entry order."""
        self.app.session_manager.current_session.account.\
            move_entry_down(self.entry)
        self.app.session_manager.save_account()
        self.app._dashboard_window.prepare_dashboard()


Builder.load_string('''
<DashboardEntry>:
    orientation: "vertical"
    size_hint: (1, None)
    height: 50

    Widget:
        size_hint: (1, .05)

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .9)

        Widget:
            size_hint: (.02, 1)

        BoxLayout:
            orientation: "horizontal"
            size_hint: (.96, 1)

            canvas:
                Color:
                    rgba: .1, .1, .1, 1
                Rectangle:
                    size: self.size
                    pos: self.pos

            Widget:
                size_hint: (.05, 1)

            BoxLayout:
                orientation: "vertical"
                size_hint: (.74, 1)

                Label:
                    id: timestamp
                    font_name: "../fonts/jd_led7.ttf"
                    text_size: self.size
                    halign: "left"
                    valign: "middle"
                    size_hint: (1, .5)

                Label:
                    id: entry_title
                    font_name: "../fonts/jd_led7.ttf"
                    text_size: self.size
                    halign: "left"
                    valign: "middle"
                    markup: True
                    size_hint: (1, .5)

            Button:
                id: edit_button
                text: "r"
                font_name: "../fonts/modernpics.otf"
                background_color: 0, 0, 0, 0
                size_hint: (.07, 1)

            Button:
                id: delete_button
                text: "I"
                font_name: "../fonts/modernpics.otf"
                background_color: 0, 0, 0, 0
                size_hint: (.07, 1)

            BoxLayout:
                orientation: "vertical"
                size_hint: (.07, 1)

                Button:
                    id: move_up_button
                    text: "-"
                    font_name: "../fonts/modernpics.otf"
                    background_color: 0, 0, 0, 0
                    size_hint: (1, .5)

                Button:
                    id: move_down_button
                    text: "/"
                    font_name: "../fonts/modernpics.otf"
                    background_color: 0, 0, 0, 0
                    size_hint: (1, .5)

        Widget:
            size_hint: (.02, 1)

    Widget:
        size_hint: (1, .05)
''')


class NewDashboardEntry(BoxLayout):
    """
    A Dashboard Entry.
    :param app: The Kivy App instance that will use this window.
    """

    def __init__(self, app, **kwargs):
        super(NewDashboardEntry, self).__init__(**kwargs)

        self.app = app

        self.entry = None

        self.ids['add_button_a'].on_press = self.add_new
        self.ids['add_button_b'].on_press = self.add_new
        self.ids['add_button_c'].on_press = self.add_new

    def switch_edit(self):
        """Switch to logedit window."""
        self.app._logedit_window.set_entry(self.entry)
        self.app._current_window.clear_widgets()
        self.app._current_window.add_widget(self.app._logedit_window)

    def add_new(self):
        """Delete entry."""
        self.app.session_manager.current_session.add_new_entry('', '')
        self.entry = self.app.session_manager.current_session.account.\
            entries[-1]
        self.switch_edit()


Builder.load_string('''
<NewDashboardEntry>:
    orientation: "vertical"
    size_hint: (1, None)
    height: 40

    Widget:
        size_hint: (1, .05)

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .9)

        Widget:
            size_hint: (.02, 1)

        BoxLayout:
            orientation: "horizontal"
            size_hint: (.96, 1)

            canvas:
                Color:
                    rgba: .2, .2, .2, 1
                Rectangle:
                    size: self.size
                    pos: self.pos

            Button:
                id: add_button_a
                background_color: 0, 0, 0, 0
                size_hint: (.05, 1)

            Button:
                id: add_button_b
                text: "Add a new entry"
                font_name: "../fonts/jd_led7.ttf"
                background_color: 0, 0, 0, 0
                size_hint: (.81, 1)

            Button:
                id: add_button_c
                text: "+"
                font_name: "../fonts/modernpics.otf"
                background_color: 0, 0, 0, 0
                size_hint: (.14, 1)

        Widget:
            size_hint: (.02, 1)

    Widget:
        size_hint: (1, .05)
''')


class DashboardWindow(BoxLayout):
    """
    Dashboard Window.
    This window is show when a session is active (The user is logged in).
    :param app: The Kivy App instance that will use this window.
    """

    def __init__(self, app, **kwargs):
        super(DashboardWindow, self).__init__(**kwargs)

        self.app = app

        self.ids['entry_list'].add_widget(NewDashboardEntry(self.app))

        self.ids['settings_button'].on_press = self.switch_settings

    def prepare_dashboard(self):
        """Prepare the dashboard."""
        session = self.app.session_manager.current_session
        if session is not None:
            self.ids['account_name'].text = f'{session.account.username!r}\'s'\
                ' entries'
        else:
            self.ids['account_name'].text = f'None\'s entries'
            return None

        self.ids['entry_list'].clear_widgets()
        for entry in session.account.entries:
            self.ids['entry_list'].add_widget(DashboardEntry(entry, self.app))
        self.ids['entry_list'].add_widget(NewDashboardEntry(self.app))

    def switch_settings(self):
        """Switch to settings window."""
        self.app._current_window.clear_widgets()
        self.app._current_window.add_widget(self.app._settings_window)


Builder.load_string('''
<DashboardWindow>:
    orientation: "vertical"

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .1)

        canvas:
            Color:
                rgba: .2, .2, .2, 1
            Rectangle:
                size: self.size
                pos: self.pos

        Widget:
            size_hint: (.0125, 1)

        Image:
            source: "../images/icon.png"
            size_hint: (.15, 1)

        Widget:
            size_hint: (.0145, 1)

        Label:
            id: account_name
            text: "None's entries"
            font_name: "../fonts/jd_led7.ttf"
            text_size: self.size
            halign: "center"
            valign: "middle"
            size_hint: (.646, 1)

        Widget:
            size_hint: (.002, 1)

        Button:
            id: settings_button
            text: "4"
            font_name: "../fonts/modernpics.otf"
            font_size: 30
            background_color: 0, 0, 0, 0
            size_hint: (.175, 1)

    ScrollView:
        size_hint: (1, .9)
        scroll_type: ['bars', 'content']

        BoxLayout:
            id: entry_list
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height

''')


class LogEditWindow(BoxLayout):
    """
    Log editting Window.
    This window is show when the user is editting a dev log.
    :param app: The Kivy App instance that will use this window.
    """

    def __init__(self, app, **kwargs):
        super(LogEditWindow, self).__init__(**kwargs)

        self.app = app

        self.ids['back_button'].on_press = self.switch_dashboard
        self.ids['save_button'].on_press = self.save_entry

        self.set_noedit()

        self.current_entry = None
        self.original_title = None
        self.original_entry = None  # Note: the entry text, not the object

        Clock.schedule_interval(self.check_change_buttons, 1e-1)

    def set_entry(self, entry: Entry):
        """
        Set the entry.
        :param entry: The Entry instance to set the entry contents of.
        """
        self.current_entry = entry
        self.original_title = entry.title
        self.original_entry = entry.entry

        self.ids['entry_title'].text = self.original_title
        self.ids['entry'].text = self.original_entry
        self.ids['entry_num'].text = "Entry number: "\
            f"{self.current_entry.entry_num}"

    def save_entry(self):
        """Save the entry."""
        self.current_entry.update(self.ids['entry_title'].text,
                                  self.ids['entry'].text)
        self.original_title = self.current_entry.title
        self.original_entry = self.current_entry.entry

        self.app.session_manager.save_account()

    def set_noedit(self):
        """Set the editor to a no edit state."""
        self.ids['back_button'].text = '<'  # Back
        self.ids['save_button'].opacity = 0
        self.ids['save_button'].disabled = True

    def set_hasedit(self):
        """Set the editor to a has edit state."""
        self.ids['back_button'].text = 'X'  # Cancel edit
        self.ids['save_button'].opacity = 1
        self.ids['save_button'].disabled = False

    def check_change_buttons(self, instance):
        """Check if user made edits to change back/cancel and save buttons."""
        if (self.current_entry is self.original_title is
                self.original_entry is None):
            return None

        if (self.ids['entry_title'].text == self.original_title and
                self.ids['entry'].text == self.original_entry):
            self.set_noedit()
        else:
            self.set_hasedit()

    def clear_window(self):
        """Clear window."""
        self.set_entry(self.current_entry)

    def switch_dashboard(self):
        """Switch to dashboard."""
        self.clear_window()

        self.app._current_window.clear_widgets()
        self.app._dashboard_window.prepare_dashboard()
        self.app._current_window.add_widget(self.app._dashboard_window)


Builder.load_string('''
<LogEditWindow>:
    orientation: "vertical"

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .075)

        Button:
            id: back_button
            font_name: "../fonts/modernpics.otf"
            font_size: 30
            background_color: 0, 0, 0, 0
            size_hint: (.1775, 1)

        Widget:
            size_hint: (.645, 1)

        Button:
            id: save_button
            text: "%"
            font_name: "../fonts/modernpics.otf"
            font_size: 30
            background_color: 0, 0, 0, 0
            size_hint: (.1775, 1)

    Label:
        id: entry_num
        text: "Entry number: null"
        font_name: "../fonts/jd_led7.ttf"
        text_size: self.size
        halign: "center"
        valign: "middle"
        size_hint: (1, .075)

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .075)

        Widget:
            size_hint: (.05, 1)

        TextInput:
            id: entry_title
            hint_text: "Entry title"
            font_name: "../fonts/jd_led7.ttf"
            foreground_color: 1, 1, 1, 1
            background_color: .2, .2, .2, 1
            text_size: self.size
            halign: "left"
            valign: "middle"
            multiline: False
            size_hint: (.9, 1)

        Widget:
            size_hint: (.05, 1)

    Widget:
        size_hint: (1, .025)

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .675)

        Widget:
            size_hint: (.05, 1)

        TextInput:
            id: entry
            hint_text: "Write your entry here..."
            font_name: "../fonts/jd_led7.ttf"
            foreground_color: 1, 1, 1, 1
            background_color: .2, .2, .2, 1
            multiline: True
            size_hint: (.9, 1)

        Widget:
            size_hint: (.05, 1)

    Widget:
        size_hint: (1, .075)

''')


class SettingsWindow(BoxLayout):
    """
    Settings window.
    This window is shown when the user is adjusting settings.
    :param app: The Kivy App instance that will use this window.
    """

    def __init__(self, app, **kwargs):
        super(SettingsWindow, self).__init__(**kwargs)

        self.app = app

        self.ids['back_button'].on_press = self.switch_dashboard
        self.ids['logout_button'].on_press = self.logout

    def switch_dashboard(self):
        """Switch to dashboard window."""
        self.app._current_window.clear_widgets()
        self.app._dashboard_window.prepare_dashboard()
        self.app._current_window.add_widget(self.app._dashboard_window)

    def logout(self):
        """Logout."""
        self.app.session_manager.stop_session()
        self.app._current_window.clear_widgets()
        self.app._current_window.add_widget(self.app._front_window)


Builder.load_string('''
<SettingsWindow>:
    orientation: "vertical"

    BoxLayout:
        orientation: "horizontal"
        size_hint: (1, .075)

        Button:
            id: back_button
            text: "<"
            font_name: "../fonts/modernpics.otf"
            font_size: 30
            background_color: 0, 0, 0, 0
            size_hint: (.175, 1)

        Widget:
            size_hint: (.825, 1)

    Image:
        source: "../images/icon.png"
        size_hint: (1, .225)

    Label:
        text: "Settings"
        font_name: "../fonts/jd_led7.ttf"
        font_size: 25
        text_size: self.size
        halign: "center"
        valign: "middle"
        size_hint: (1, .075)

    Widget:
        size_hint: (1, .1)

    BoxLayout:
        size_hint: (1, .075)

        Widget:
            size_hint: (.15, 1)

        Button:
            id: logout_button
            text: "Log Out"
            font_name: "../fonts/jd_led7.ttf"
            text_size: self.size
            halign: "center"
            valign: "middle"
            size_hint: (.7, 1)

        Widget:
            size_hint: (.15, 1)

    Widget:
        size_hint: (1, .375)

    Widget:
        size_hint: (1, .075)
''')


class DevLogs(App):
    """Main DevLogs App."""

    def __init__(self, **kwargs):
        super(DevLogs, self).__init__(**kwargs)

        self.icon = "../images/icon.png"

        # Init Session Manager

        self.session_manager = SessionManager()

        # Init windows

        self._front_window = FrontWindow(self)
        self._login_window = LoginWindow(self)
        self._signup_window = SignUpWindow(self)
        self._dashboard_window = DashboardWindow(self)
        self._logedit_window = LogEditWindow(self)
        self._settings_window = SettingsWindow(self)

        self._current_window = BoxLayout()

        self._current_window.add_widget(self._front_window)

    def build(self):
        """Build the main DevLogs App."""
        return self._current_window
