class Bill(Screen):

    selected_date = None

    def on_pre_enter(self):
        self.ids.bill_amount.text = ""
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
                "on_release": lambda x=i: self.set_item(x),
            } for i in categories
        ]
        self.menu = MDDropdownMenu(caller=item, items=menu_items, width_mult=4)
        self.menu.open()

    def set_item(self, text_item):
        self.ids.drop_item.text = text_item
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