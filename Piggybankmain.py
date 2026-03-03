# importing necessary libraries
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, FadeTransition
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivymd.uix.dialog import MDDialog, MDDialogButtonContainer, MDDialogHeadlineText, MDDialogContentContainer
from kivy.animation import Animation
from db import get_connection, create_table, add_user, verify_user, get_user_stats, add_income, add_expense, add_goal, get_goals, update_goal_progress


class MainScreen(Screen):
    pass


class SplashScreen(Screen):

    def on_enter(self, *args):
        self.ids.s_progress.value = 0
        anime = Animation(value=100, duration=1.5, t="linear")

        anime.bind(on_complete=self.switch_to_main)

        anime.start(self.ids.s_progress)

        self.manager.transition = FadeTransition(duration=0.5)

    def switch_to_main(self, *args):

        self.manager.current = "main"

        self.manager.transition = NoTransition()


class LoginScreen(Screen):
    def on_pre_enter(self):
        self.ids.email.text = ""
        self.ids.password.text = ""

    def login_process(self):
        email = self.ids.email.text
        password = self.ids.password.text

        if not email or not password:
            print("Please fill in all fields")
            return

        try:
            conn = get_connection()
            user_id = verify_user(conn, email, password)
            conn.close()

            if user_id is not None:
                MDSnackbar(
                    MDSnackbarText(text="Login Successful! Welcome back."),
                    y="24dp",
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                ).open()

                app = MDApp.get_running_app()
                app.current_user_id = user_id

                app.update_dashboard()

                self.ids.email.text = ""
                self.ids.password.text = ""
                self.manager.current = "main"
            else:
                MDSnackbar(
                    MDSnackbarText(
                        text="Invalid email or password. Please try again."),
                    y="24dp",
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                ).open()

        except Exception as e:
            print(f"Login error: {e}")


class AddFund(Screen):
    def save_income(self):
        amount = self.ids.fund_amount.text
        app = MDApp.get_running_app()

        if amount and app.current_user_id:
            conn = get_connection()
            add_income(conn, app.current_user_id, float(amount), "Deposit")
            conn.close()

            self.ids.fund_amount.text = ""
            app.update_dashboard()
            self.manager.current = "main"


class Bill(Screen):

    def open_category_menu(self, item):
        # List of categories for bills
        categories = ["Rent", "Water Bill", "Electricty", "Car Payment",
                      "Transpot", "Entertemnt", "grocery", "saveings"]

        menu_items = [
            {
                "text": i,
                "on_release": lambda x=i: self.set_item(x),
            } for i in categories
        ]
        self.menu = MDDropdownMenu(caller=item, items=menu_items, width_mult=4)
        self.menu.open()

    def set_item(self, text_item):
        self.ids.drop_item.text = text_item  # Update the button text
        self.menu.dismiss()

    def save_expense(self):
        amount = self.ids.bill_amount.text
        category = self.ids.drop_item.text  # Get the selected category
        app = MDApp.get_running_app()

        if amount and app.current_user_id:
            conn = get_connection()

            add_expense(conn, app.current_user_id, float(amount), category)
            conn.close()

            self.ids.bill_amount.text = ""
            self.ids.drop_item.text = "Select Category"
            app.update_dashboard()
            self.manager.current = "main"


class Target(Screen):

    def on_enter(self):
        self.display_goals()

    def display_goals(self):
        self.ids.goal_container.clear_widgets()
        app = MDApp.get_running_app()

        with get_connection() as conn:
            goals = get_goals(conn, app.current_user_id)

        for g_id, name, target, saved in goals:
            percentage = (saved / target) if target > 0 else 0

            goal_card = MDCard(
                orientation='vertical',
                adaptive_height=True,
                padding="15dp",
                spacing="10dp",
                style="elevated",
                md_bg_color=app.theme_cls.surfaceColor
            )
            goal_card.add_widget(
                MDLabel(
                    text=f"{name}",
                    style="title-medium"
                )
            )

            goal_card.add_widget(
                MDLabel(
                    text=f"${saved:,.2f} of ${target:,.2f}",
                    style="body-small"
                )
            )

            progress = MDLinearProgressIndicator(
                value=percentage * 100,
                size_hint_y=None,
                height="10dp"
            )
            goal_card.add_widget(progress)
            self.ids.goal_container.add_widget(goal_card)


class RegisterScreen(Screen):

    def on_pre_enter(self):
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

                MDSnackbar(
                    MDSnackbarText(
                        text=f"Account created for {name}! Please login."),
                    y="24dp",
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                ).open()

                self.manager.current = "login"
            except Exception:
                MDSnackbar(
                    MDSnackbarText(
                        text="Error: Email might already be registered."),
                    y="24dp",
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                ).open()
        else:
            print("error")


class PiggyBankLauncher(MDApp):
    current_user_id = None
    menu = None

    def open_account_menu(self, button):
        if self.current_user_id:
            menu_items = [
                {
                    "text": "Logout",
                    "on_release": lambda: self.logout(),
                },
            ]
        else:
            menu_items = [
                {"text": "Login Page",
                 "on_release": lambda: self.menu_callback("login")},
                {"text": "Register Page",
                    "on_release": lambda: self.menu_callback("register")},
            ]

        self.menu = MDDropdownMenu(
            caller=button, items=menu_items, width_mult=4)
        self.menu.open()

    def menu_callback(self, screen_name):
        self.menu.dismiss()
        self.root.current = screen_name

    def logout(self):
        self.current_user_id = None

        main_screen = self.root.get_screen('main')
        main_screen.ids.balance_label.text = "$0.00"
        main_screen.ids.total_label.text = "$0.00"

        if self.menu:
            self.menu.dismiss()

        self.root.current = "login"

    def update_dashboard(self):

        if self.current_user_id:
            conn = get_connection()
            total_in, total_ex, balance = get_user_stats(
                conn, self.current_user_id)
            conn.close()

            main_screen = self.root.get_screen('main')

            main_screen.ids.balance_label.text = f"${balance:,.2f}"

            main_screen.ids.total_label.text = f"Total Spent: ${total_ex:,.2f}"

    def build(self):
        connection = get_connection()
        create_table(connection)
        connection.close()
        # theme
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        # builder
        Builder.load_file("splashscreen.kv")
        Builder.load_file("mainscreen.kv")
        Builder.load_file("loginscreen.kv")
        Builder.load_file("registerscreen.kv")
        Builder.load_file("addfund.kv")
        Builder.load_file("bill.kv")
        Builder.load_file("target.kv")
        # screens
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(AddFund(name="addfund"))
        sm.add_widget(Bill(name="bill"))
        sm.add_widget(Target(name="target"))
        sm.current = "splash"
        return sm

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
