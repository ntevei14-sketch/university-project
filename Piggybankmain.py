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
from db import delete_goal_from_db, get_connection, create_table, add_user, verify_user, get_user_stats, add_income, add_expense, add_goal, get_goals, update_goal_progress, get_expenses
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from utlity import is_valid_email
from kivy.factory import Factory
from kivymd.uix.pickers import MDModalDatePicker
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemTertiaryText
from plyer import notification
from datetime import datetime


class MainScreen(Screen):

    def on_enter(self):
        app = MDApp.get_running_app()
        app.update_dashboard()
        app.check_for_notifications()


class ImageGrid(RectangularRippleBehavior, ButtonBehavior, MDBoxLayout):
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

    def on_pre_enter(self, *args):
        self.ids.email.text = ""
        self.ids.password.text = ""

    def login_process(self):
        email = self.ids.email.text
        password = self.ids.password.text

        if not is_valid_email(email):
            MDSnackbar(
                MDSnackbarText(text="Please enter a valid email address."),
                y="24dp",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            ).open()
            return

        if not email or not password:
            MDSnackbar(
                MDSnackbarText(text="please fill the empty fileds"),
                y="24dp",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            ).open()
            return

        try:
            conn = get_connection()
            user_id = verify_user(conn, email, password)
            conn.close()

            if user_id:
                MDSnackbar(
                    MDSnackbarText(text=f"Login Successful! Welcome back "),
                    y="24dp",
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                ).open()

                app = MDApp.get_running_app()
                app.current_user_id = user_id
                app.update_dashboard()
                app.check_for_notifications()
                self.manager.current = "main"
            else:
                MDSnackbar(
                    MDSnackbarText(
                        text="Invalid email or password. Please try again."),
                    y="24dp",
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                ).open()

        except Exception:
            return


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

    selected_date = None

    def on_pre_enter(self):
        self.ids.drop_item.text = "Select Category"
        self.ids.date_label.text = "No Date Selected"
        self.selected_date = None

    def open_category_menu(self, item):
        # List of categories for bills
        categories = ["Rent", "Water Bill", "Electricty", "Car Payment",
                      "Transpot", "Entertemnt", "grocery", "Other"]

        menu_items = [
            {
                "text": i,
                "leading_icon": "tag-outline",
                "on_release": lambda x=i: self.set_item(x),
            } for i in categories
        ]
        self.menu = MDDropdownMenu(caller=item, items=menu_items, width_mult=4)
        self.menu.open()

    def set_item(self, text_item):
        self.ids.drop_item.text = f"Category: {text_item}"
        self.menu.dismiss()

    def show_date_picker(self):
        date_dialog = MDModalDatePicker()
        date_dialog.bind(on_ok=self.on_ok, on_cancel=self.on_cancel)
        date_dialog.open()

    def on_ok(self, instance):
        dates = instance.get_date()
        if dates:
            self.selected_date = dates[0].strftime('%Y-%m-%d')
            self.ids.date_label.text = f"Due Date: {self.selected_date}"
        instance.dismiss()

    def on_cancel(self, instance):
        instance.dismiss()

    def save_expense(self):
        amount = self.ids.bill_amount.text
        category = self.ids.drop_item.text
        app = MDApp.get_running_app()

        if not amount or category == "Select Category" or not self.selected_date:
            MDSnackbar(
                MDSnackbarText(
                    text="Please fill all fields and select category and date."),
                y="24dp",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            ).open()
            return
        if amount and app.current_user_id:
            conn = get_connection()

            add_expense(conn, app.current_user_id, float(
                amount), category, self.selected_date)
            conn.close()

            self.ids.bill_amount.text = ""
            self.ids.drop_item.text = "Select Category"
            self.ids.date_label.text = "No Date Selected"
            app.update_dashboard()
            self.manager.current = "main"


class Target(Screen):

    def save_goal(self):
        name = self.ids.goal_name.text
        amount = self.ids.target_amount.text
        app = MDApp.get_running_app()

        if name and amount and app.current_user_id:
            try:
                conn = get_connection()
                add_goal(conn, app.current_user_id, name, float(amount))
                conn.close()

                self.ids.goal_name.text = ""
                self.ids.target_amount.text = ""

                MDSnackbar(MDSnackbarText(
                    text="Goal created successfully!")).open()

            except ValueError:
                MDSnackbar(MDSnackbarText(
                    text="Please enter a valid number")).open()


class GoalsPreview(Screen):
    fund_dialog = None
    current_funding_id = None

    def on_enter(self):
        self.display_all_goals()

    def display_all_goals(self):
        container = self.ids.all_goals_container
        container.clear_widgets()
        app = MDApp.get_running_app()

        with get_connection() as conn:
            goals = get_goals(conn, app.current_user_id)

        for g_id, name, target, saved in goals:
            perc = (saved / target) if target > 0 else 0

            item = Factory.GoalItem()
            item.goal_id = g_id
            item.goal_name = name
            item.saved_text = f"Saved: ${saved:,.2f} / Goal: ${target:,.2f}"
            item.progress_value = min(perc * 100, 100)
            container.add_widget(item)

    def delete_goal(self, goal_id):
        with get_connection() as conn:
            delete_goal_from_db(conn, goal_id)
        self.display_all_goals()
        MDSnackbar(MDSnackbarText(text="Goal deleted.")).open()

    def open_fund_dialog(self, goal_id):
        self.current_funding_id = goal_id

        self.amount_input = Factory.MDTextField(
            hint_text="Amount",
            input_filter="float"
        )

        self.fund_dialog = MDDialog(
            MDDialogHeadlineText(text="Add Funds"),
            MDDialogContentContainer(
                MDBoxLayout(
                    self.amount_input,
                    orientation="vertical",
                    adaptive_height=True
                )
            ),
            MDDialogButtonContainer(
                Factory.MDButton(
                    Factory.MDButtonText(text="Cancel"),
                    style="text",
                    on_release=lambda x: self.fund_dialog.dismiss()
                ),
                Factory.MDButton(
                    Factory.MDButtonText(text="Save"),
                    style="tonal",
                    on_release=self.confirm_funding
                ),
            )
        )
        self.fund_dialog.open()

    def confirm_funding(self, *args):
        try:
            amt = float(self.amount_input.text or 0)
        except ValueError:
            return

        app = MDApp.get_running_app()
        is_completed = False

        with get_connection() as conn:
            _, _, balance = get_user_stats(conn, app.current_user_id)

            if amt > balance:
                MDSnackbar(MDSnackbarText(text="Insufficient Balance!")).open()
                return

            add_expense(conn, app.current_user_id, amt,
                        "Goal Funding", "Internal Transfer")
            update_goal_progress(conn, self.current_funding_id, amt)

            cursor = conn.cursor()
            cursor.execute(
                "SELECT current_saved, target_amount FROM goals WHERE id = ?",
                (self.current_funding_id,)
            )
            goal_data = cursor.fetchone()

            if goal_data:
                saved, target = goal_data
                if saved >= target:
                    delete_goal_from_db(conn, self.current_funding_id)
                    is_completed = True

        self.fund_dialog.dismiss()
        self.display_all_goals()
        app.update_dashboard()

        if is_completed:
            MDSnackbar(MDSnackbarText(
                text="Goal Reached! Target deleted.")).open()
        else:
            MDSnackbar(MDSnackbarText(text="Funds added!")).open()


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

        if not is_valid_email(email):
            MDSnackbar(
                MDSnackbarText(text="Please enter a valid email address."),
                y="24dp",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            ).open()
            return

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
                        text="there is already an existed email, please try another one"),
                    y="24dp",
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                ).open()
        else:
            MDSnackbar(
                MDSnackbarText(
                    text="please fill the empty fileds"),
                y="24dp",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            ).open()


class NotificationManager:

    def __init__(self, db_path="user_data.db"):
        self.db_path = db_path

    def check_due_bills(self, user_id):

        today = datetime.now().strftime('%Y-%m-%d')

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT category, amount FROM expenses WHERE user_id = ? AND due_date = ?",
                (user_id, today)
            )
            due_items = cursor.fetchall()
            conn.close()

            for category, amount in due_items:
                self.send_push(category, amount)

        except Exception as e:
            print(f"Notification System Error: {e}")

    def send_push(self, bill_name, amount):

        clean_name = str(bill_name).replace("Category: ", "").title()

        notification.notify(
            title="Its pay time",
            message=f"Your {clean_name} bill of ${amount:,.2f} is due today.",
            app_name="PiggyBank",
            timeout=8
        )


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
        main_screen.ids.balance_label.text = "Balance:$0.00"
        main_screen.ids.total_label.text = "Saveings:$0.00"
        main_screen.ids.bills_history_list.clear_widgets()
        main_screen.ids.goals_preview_list.clear_widgets()
        if self.menu:
            self.menu.dismiss()

        self.root.current = "main"

    def update_dashboard(self):
        if self.current_user_id:

            conn = get_connection()
            total_in, total_ex, balance = get_user_stats(
                conn, self.current_user_id)
            bills_data = get_expenses(conn, self.current_user_id)
            goals_data = get_goals(conn, self.current_user_id)
            conn.close()

            main_screen = self.root.get_screen('main')

            main_screen.ids.balance_label.text = f"Balance: ${total_in:,.2f}"
            main_screen.ids.total_label.text = f"Savings: ${balance:,.2f}"

            history_list = main_screen.ids.bills_history_list
            history_list.clear_widgets()

            for b_id, amount, category, due_date in bills_data:

                item = MDListItem(
                    MDListItemHeadlineText(text=str(category)),
                    MDListItemSupportingText(text=f"Due: {due_date}"),
                    MDListItemTertiaryText(text=f"${amount:,.2f}"),
                    height="72dp",
                    size_hint_y=None
                )
                history_list.add_widget(item)

            goals_preview = main_screen.ids.goals_preview_list
            goals_preview.clear_widgets()

            for g_id, name, target, saved in goals_data[:3]:

                percentage = (saved / target) if target > 0 else 0
                val = min(percentage * 100, 100)
                goal_card = MDCard(
                    orientation='vertical',
                    size_hint=(1, None),
                    height="55dp",
                    padding="8dp",
                    spacing="4dp",
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color=self.theme_cls.surfaceColor
                )

                goal_card.add_widget(MDLabel(text=name, style="label-medium"))
                goal_card.add_widget(
                    MDLabel(text=f"${saved:,.0f}/${target:,.0f}", style="label-small"))

                progress = MDLinearProgressIndicator(
                    value=val,
                    size_hint_y=None,
                    height="4dp"
                )
                goal_card.add_widget(progress)
                goals_preview.add_widget(goal_card)

    def build(self):
        connection = get_connection()
        create_table(connection)
        connection.close()
        # theme
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Pink"
        # notfication manager
        self.notif_manager = NotificationManager()
        # builder
        Builder.load_file("splashscreen.kv")
        Builder.load_file("mainscreen.kv")
        Builder.load_file("loginscreen.kv")
        Builder.load_file("registerscreen.kv")
        Builder.load_file("addfund.kv")
        Builder.load_file("bill.kv")
        Builder.load_file("target.kv")
        Builder.load_file("goalspreview.kv")
        # screens
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(AddFund(name="addfund"))
        sm.add_widget(Bill(name="bill"))
        sm.add_widget(Target(name="target"))
        sm.add_widget(GoalsPreview(name="goalspreview"))
        sm.current = "splash"

        return sm

    def check_for_notifications(self):
        if self.current_user_id:
            self.notif_manager.check_due_bills(self.current_user_id)

    # function to switch between light and dark mode

    def switch_theme_style(self):
        self.theme_cls.primary_palette = (
            "Pink" if self.theme_cls.primary_palette == "Indigo" else "Indigo"
        )
        self.theme_cls.theme_style = (
            "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        )


if __name__ == "__main__":
    PiggyBankLauncher().run()
