   def on_enter(self):
        self.display_all_goals()

    def display_all_goals(self):
        container = self.ids.all_goals_container
        container.clear_widgets()

        app = MDApp.get_running_app()
        if not app.current_user_id:
            return

        with get_connection() as conn:
            goals = get_goals(conn, app.current_user_id)

        for g_id, name, target, saved in goals:
            perc = (saved / target * 100) if target > 0 else 0

            item = Builder.template(
                'GoalItem',
                goal_id=g_id,
                goal_name=name,
                saved_text=f"${saved:,.2f} / ${target:,.2f}",
                progress_value=min(perc, 100)
            )
            container.add_widget(item)

    def delete_goal(self, goal_id):

        print(f"Goal {goal_id} has been deleted.")
        self.display_all_goals()

    def open_fund_dialog(self, goal_id):

        print(f"Logic to add funds to goal ID: {goal_id}")
