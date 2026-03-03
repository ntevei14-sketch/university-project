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