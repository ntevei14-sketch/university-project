# importing the library needed

import sqlite3
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash

# variable for the password hasher

ph = PasswordHasher()

# connection


def get_connection(filename="user_data.db"):
    try:
        return sqlite3.connect(filename)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

# creating the table for the user data


def create_table(connection):

    userdata_table = """CREATE TABLE IF NOT EXISTS user_data (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL
    );"""
    try:
        with connection:
            connection.execute(userdata_table)
    except Exception as e:
        print(f"Error creating table: {e}")
        raise
# function to add user data to the database


def add_user(connection, name: str, password: str, email: str, phone: str):
    password_hash = ph.hash(password)
    insert_query = """INSERT INTO user_data (name, password_hash, email, phone) VALUES (?, ?, ?, ?);"""
    try:
        with connection:
            connection.execute(
                insert_query, (name, password_hash, email, phone))
            print(f"User {name} added successfully.")
    except Exception as e:
        print(f"Error adding user: {e}")
        raise

# verify user


def verify_user(connection, email, password):
    query = "SELECT password_hash FROM user_data WHERE email = ?;"
    cursor = connection.execute(query, (email,))
    row = cursor.fetchone()

    if row:
        stored_hash = row[0]
        try:
            ph.verify(stored_hash, password)
            return True
        except (VerifyMismatchError, InvalidHash):
            return False
    return False

# the main table for the user data


def main():

    connection = get_connection("user_data.db")
    try:
        # CREATE TABLE
        create_table(connection)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
