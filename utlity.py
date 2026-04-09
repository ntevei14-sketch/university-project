import re


def is_valid_email(email):
    # Simple yet effective regex for email validation
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Checking if email is not empty and matches regex
    if email and re.match(regex, email):
        return True
    return False
