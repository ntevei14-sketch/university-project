        except Exception as e:
            print(f"Notification System Error: {e}")

    def send_push(self, bill_name, amount):

        clean_name = str(bill_name).replace("Category: ", "").title()

        notification.notify(
            title="Its pay time",
            message=f"Your {clean_name} bill of ${amount:,.2f} is due today.",
            app_name="PiggyBank",
            timeout=4
        )


class Saveingsview(Screen):
    def on_enter(self):
        self.update_view()
