# importing the library needed

import sqlite3
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash

# variable for the password hasher

ph = PasswordHasher()

# connection


def get_connection(filename="user_data.db"):
    try:
        conn = sqlite3.connect(filename)
        # Add this line to make sure deleting a user affects their data if needed
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

# creating the table for the user data


def create_table(connection):
    try:
        with connection:
            # Table 1: Users
            connection.execute("""
                CREATE TABLE IF NOT EXISTS user_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL
                );""")

            # Table 2: Incomes
            connection.execute("""
                CREATE TABLE IF NOT EXISTS incomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL NOT NULL,
                    source TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_data (id)
                );""")

            # Table 3: Expenses
            connection.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL NOT NULL,
                    category TEXT,
                    due_date TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_data (id)
                );""")
            # Table 4: Goals
            connection.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    goal_name TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    current_saved REAL DEFAULT 0.0,
                    FOREIGN KEY (user_id) REFERENCES user_data (id)
                );""")
    except Exception as e:
        print(f"Error creating table: {e}")
        raise

# geting the user stat(income)


def get_user_stats(connection, user_id):
    cursor = connection.cursor()

    cursor.execute(
        "SELECT SUM(amount) FROM incomes WHERE user_id = ?", (user_id,))
    res_in = cursor.fetchone()
    total_income = res_in[0] if res_in and res_in[0] else 0.0

    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id = ?", (user_id,))
    res_ex = cursor.fetchone()
    total_expense = res_ex[0] if res_ex and res_ex[0] else 0.0

    balance = total_income - total_expense
    return total_income, total_expense, balance

# adding user


def add_user(connection, name: str, password: str, email: str, phone: str):
    password_hash = ph.hash(password)
    insert_query = """INSERT INTO user_data (name, password_hash, email, phone) VALUES (?, ?, ?, ?);"""
    try:
        with connection:
            connection.execute(
                insert_query, (name, password_hash, email.lower(), phone))
            print(f"User {name} added successfully.")
    except Exception as e:
        print(f"Error adding user: {e}")
        raise

# verify user


def verify_user(connection, email, password):

    query = "SELECT id, password_hash FROM user_data WHERE email = ?;"
    cursor = connection.execute(query, (email,))
    row = cursor.fetchone()

    if row:
        user_id, stored_hash = row
        try:
            ph.verify(stored_hash, password)
            return user_id
        except (VerifyMismatchError, InvalidHash):
            return None
    return None

# adding income function


def add_income(connection, user_id, amount, source="General"):
    with connection:
        connection.execute(
            "INSERT INTO incomes (user_id, amount, source) VALUES (?, ?, ?);",
            (user_id, amount, source)
        )

# adding expense function


def add_expense(connection, user_id, amount, category, due_date):
    with connection:
        connection.execute(
            "INSERT INTO expenses (user_id, amount, category, due_date) VALUES (?, ?, ?, ?);",
            (user_id, amount, category, due_date)
        )

# goal function


def add_goal(connection, user_id, name, target):
    with connection:
        connection.execute(
            "INSERT INTO goals (user_id, goal_name, target_amount) VALUES (?, ?, ?);",
            (user_id, name, target)
        )


def get_goals(connection, user_id):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, goal_name, target_amount, current_saved FROM goals WHERE user_id = ?", (user_id,))
    return cursor.fetchall()


def update_goal_progress(connection, goal_id, amount):
    with connection:
        connection.execute(
            "UPDATE goals SET current_saved = current_saved + ? WHERE id = ?",
            (amount, goal_id)
        )


def get_expenses(connection, user_id):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, amount, category, date FROM expenses WHERE user_id = ? ORDER BY date DESC",
        (user_id,)
    )
    return cursor.fetchall()

# main


def main():

    connection = get_connection("user_data.db")
    try:
        # CREATE TABLE
        create_table(connection)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
