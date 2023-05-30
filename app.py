import mysql.connector
from flask import Flask, render_template, request
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



def check_password_strength(username, email, birthdate, password):
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
        return f"Weak password. It contains parts of your username, email, or birthdate.\n password complexity = {complexity} \n needed time to crack = {crack_time}"

    # Verify password strength based on criteria
    has_length = len(password) >= 8
    has_upper = re.search(r"[A-Z]", password) is not None
    has_lower = re.search(r"[a-z]", password) is not None
    has_digit = re.search(r"\d", password) is not None
    has_symbol = re.search(r"[?!@#$%^&*():;,./_=+\-]", password) is not None

    if has_length and has_upper and has_lower and has_digit and has_symbol:
        complexity = 95 ** len(password)
        crack_time = calculate_crack_time(complexity)
        return f"Strong password, Complexity level = {complexity}, Time needed to crack: {crack_time}"
    else:
        complexity = 95 ** len(password)
        feedback = []
        if not has_length:
            feedback.append("Password should have at least 8 characters.\n")
        if not has_upper:
            feedback.append("Password should have at least one uppercase letter.\n")
        if not has_lower:
            feedback.append("Password should have at least one lowercase letter.\n")
        if not has_digit:
            feedback.append("Password should have at least one digit.\n")
        if not has_symbol:
            feedback.append("Password should have at least one symbol (!@#$%^&*()).\n")

        crack_time = calculate_crack_time(complexity)

        return (
                "Weak password. "
                + ", ".join(feedback)
                + f", Complexity level = {complexity}, Time needed to crack: {crack_time}"
        )


def calculate_crack_time(complexity):
    # Estimate time to crack the password based on complexity
    seconds_per_attempt = 1e-10  # Assuming 10 billion offline hash attempts per second
    crack_time_seconds = complexity * seconds_per_attempt

    crack_time_years = crack_time_seconds / (60 * 60 * 24 * 365)
    crack_time_months = crack_time_seconds / (60 * 60 * 24 * 30)
    crack_time_weeks = crack_time_seconds / (60 * 60 * 24 * 7)
    crack_time_days = crack_time_seconds / (60 * 60 * 24)

    years = int(crack_time_years)
    months = int(crack_time_months % 12)
    weeks = int(crack_time_weeks % 4)
    days = int(crack_time_days % 7)
    if crack_time_seconds < 1:
        return "few seconds"  # Return a default value for short weak passwords

    crack_time_str = ''
    if years > 0:
        crack_time_str += f'{years} year(s) '
    if months > 0:
        crack_time_str += f'{months} month(s) '
    if weeks > 0:
        crack_time_str += f'{weeks} week(s) '
    if days > 0:
        crack_time_str += f'{days} day(s)'

    return crack_time_str.strip()


# Flask application
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check_password', methods=['POST'])
def check_password():
    # Retrieve form data
    username = request.form['username']
    email = request.form['email']
    birthdate = request.form['birthdate']
    password = request.form['password']

    # Perform password strength check and generate alert message
    alert_message = check_password_strength(username, email, birthdate, password)

    # Return the alert message as a JavaScript response
    return f'<script>alert("{alert_message}"); window.history.back();</script>'


if __name__ == '__main__':
    app.run(debug=True)
