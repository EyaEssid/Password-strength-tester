import tkinter as tk
from tkinter import messagebox
import mysql.connector
import re

# Connect to the MySQL server
conn = mysql.connector.connect(
    user='root',
    password='root',
    host='127.0.0.1',
    database='common_passwords',
    auth_plugin='mysql_native_password'
)

# Create a cursor object to execute queries
cursor = conn.cursor()

# Execute the SELECT query
cursor.execute("SELECT passwords FROM common_password;")

# Fetch all the results
results = cursor.fetchall()

# Store the passwords in a list
common_passwords = [row[0] for row in results]

# Close the cursor and connection
cursor.close()
conn.close()


def check_password_strength():
    username = username_entry.get()
    email = email_entry.get()
    birthdate = birthdate_entry.get()
    password = password_entry.get()

    # Evaluate the password
    result = evaluate_password(username, email, birthdate, password)

    # Show a message box with the result
    messagebox.showinfo("Password Strength Checker", result)


def evaluate_password(username, email, birthdate, password):
    # Check if the password exists in the common passwords list
    if password.lower() in common_passwords:
        return "Password is weak. It is a common password."

    # Verify username, email, and birthdate existence in password
    if (
        username and any(part.lower() in password.lower() for part in username.split()) or
        email and any(part.lower() in password.lower() for part in re.split(r"[\W_]+", email)) or
        birthdate and any(part in password for part in re.findall(r"\d+", birthdate))
    ):
        complexity = 0
        crack_time = "less than a second"
        return f"Weak password. It contains parts of your username, email, or birthdate.\nPassword complexity: {complexity}\nTime needed to crack: {crack_time}"

    # Verify password strength based on criteria
    has_length = len(password) >= 8
    has_upper = re.search(r"[A-Z]", password) is not None
    has_lower = re.search(r"[a-z]", password) is not None
    has_digit = re.search(r"\d", password) is not None
    has_symbol = re.search(r"[?!@#$%^&*():;,./_=+\-]", password) is not None

    if has_length and has_upper and has_lower and has_digit and has_symbol:
        complexity = 95 ** len(password)
        crack_time = calculate_crack_time(complexity)
        return f"Strong password.\nPassword complexity: {complexity}\nTime needed to crack: {crack_time}"
    else:
        complexity = 95 ** len(password)
        feedback = []
        if not has_length:
            feedback.append("Password should have at least 8 characters.")
        if not has_upper:
            feedback.append("Password should have at least one uppercase letter.")
        if not has_lower:
            feedback.append("Password should have at least one lowercase letter.")
        if not has_digit:
            feedback.append("Password should have at least one digit.")
        if not has_symbol:
            feedback.append("Password should have at least one symbol (!@#$%^&*()).")

        crack_time = calculate_crack_time(complexity)

        return (
            "Weak password.\n"
            + "\n".join(feedback)
            + f"\nPassword complexity: {complexity}\nTime needed to crack: {crack_time}"
        )


def calculate_crack_time(complexity):
    seconds = complexity / 1000000000
    if seconds < 1:
        return "less than a second"
    elif seconds < 60:
        return "less than a minute"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''}"


# Create the main window
window = tk.Tk()
window.title("Password Strength Checker")

# Create labels and entry fields
username_label = tk.Label(window, text="Username:")
username_label.pack()
username_entry = tk.Entry(window)
username_entry.pack()

email_label = tk.Label(window, text="Email:")
email_label.pack()
email_entry = tk.Entry(window)
email_entry.pack()

birthdate_label = tk.Label(window, text="Birthdate (DD-MM-YYYY):")
birthdate_label.pack()
birthdate_entry = tk.Entry(window)
birthdate_entry.pack()

password_label = tk.Label(window, text="Password:")
password_label.pack()
password_entry = tk.Entry(window, show="*")
password_entry.pack()

# Create a button to check the password strength
check_button = tk.Button(window, text="Check", command=check_password_strength)
check_button.pack()

# Start the main loop
window.mainloop()
