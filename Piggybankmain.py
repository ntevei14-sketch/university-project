# importing necessary libraries
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
# from kivymd.uix.menu import MDDropdownMenu
# from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from db import get_connection, create_table, add_user, verify_user


class MainScreen(Screen):
    pass


class LoginScreen(Screen):

    def on_leave_login(self):
        self.ids.email.text = ""
        self.ids.password.text = ""

    def login_process(self):
        email = self.ids.email.text
        password = self.ids.password.text

        if not email or not password:
            print("please check your password or email")
            return

        try:
            conn = get_connection()
            is_valid = verify_user(conn, email, password)
            conn.close()

            if is_valid:
                print("you are logged")
                self.manager.current = "main"
            else:
                print("check your email and password")

        except Exception as e:
            print(f"error: {e}")


class AddFund(Screen):
    pass


class RegisterScreen(Screen):

    def on_leave_register(self):
        self.ids.r_username.text = ""
        self.ids.r_email.text = ""
        self.ids.r_password.text = ""
        self.ids.r_phone.text = ""

    def signup_user(self):

        name = self.ids.r_username.text
        email = self.ids.r_email.text
        password = self.ids.r_password.text
        phone = self.ids.r_phone.text

        if name and email and password:
            try:

                conn = get_connection()
                add_user(conn, name, password, email, phone)
                conn.close()

                print("you have been registerd")

                self.manager.current = "login"
            except Exception as e:
                print(f"something went worng {e}")
        else:
            print("please fill the empty filed")
 # function to toggle password visibility in the login screen and register screen(not working need to do)

    def toggle_password_visibility(self):

        password_field = self.ids.r_password
        eye_button = self.ids.r_password.ids.eye_button

        if password_field.password:
            password_field.password = False  # Show the password
            eye_button.icon = "eye"  # Change icon to "eye" (show)
        else:
            password_field.password = True  # Hide the password
            eye_button.icon = "eye-off"  # Change icon to "eye-off" (hide)


class PiggyBankLauncher(MDApp):

    def build(self):

        connection = get_connection()
        create_table(connection)
        connection.close()

        # theme
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        # builder
        Builder.load_file("mainscreen.kv")
        Builder.load_file("loginscreen.kv")
        Builder.load_file("registerscreen.kv")
        Builder.load_file("addfund.kv")
        # screens
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(AddFund(name="addfund"))
        return sm

        # test buttons
    def logger(self):
        print("Login button pressed")

    def register(self):
        print("Register button pressed")

    def show_account_menu(self):
        print("Account menu button pressed")

    # function to switch between light and dark mode

    def switch_theme_style(self):
        self.theme_cls.primary_palette = (
            "Pink" if self.theme_cls.primary_palette == "Indigo" else "Indigo"
        )
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )


if __name__ == "__main__":
    PiggyBankLauncher().run()
