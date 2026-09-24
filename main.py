from flask import Flask, render_template, request, redirect, url_for, session
from itsdangerous import URLSafeSerializer
import sqlite3


app = Flask(__name__)
app.secret_key = "DishScope-000"

@app.get("/")
def home ():
    if request.method == 'GET':
        return render_template("homepage.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    name = ""
    errors = []
    if request.method == "POST":
        role = request.form.get("role")
        connection = sqlite3.connect('test.db')
        cursor = connection.cursor()
        table2 = 'drop table users'
        table = '''create table if not exists users(
                ID integer primary key autoincrement,
                name text not null,
                password text not null,
                email text not null,
                role text not null
        )'''
        input_insert = "insert into users(name, password, email, role) values(?, ?, ?, ?)"
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        table_username = request.form.get("name", "").strip()
        table_password = (request.form.get("password",) or "").strip()
        table_email = request.form.get("email")
        table_vendor_name = request.form.get("vendor_name")
        table_vendor_location = request.form.get("vendor_location")

                

        if not table_username:
            error_name = "Username is required"
            return render_template("register.html", error_name=error_name)
        elif not table_password:
            error_pass = "Password is required"
            return render_template("register.html", table_username=table_username, error_pass=error_pass)
        elif not table_email:
            error_email = "Email is required"
            return render_template("register.html", table_username=table_username, table_password=table_password, error_email=error_email)
        else:
            cursor.execute(table)
            cursor.execute(input_insert, (table_username, password, email, role))
            connection.commit()
            if role == "vendor":
                vendor_table = '''create table if not exists vendors(
                ID integer primary key autoincrement,
                name text not null,
                vendor_name text not null,
                vendor_location text not null,
                role text not null
        )'''
                input_insert_vendor = "insert into vendors(name, vendor_name, vendor_location, role) values(?, ?, ?, ?)"
                cursor.execute(vendor_table)
                cursor.execute(input_insert_vendor, (table_username, table_vendor_name, table_vendor_location, role))
            connection.commit()
            connection.close()
            return f'Hello, {name}'
            


    return render_template('register.html')
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        connection = sqlite3.connect('test.db')
        cursor = connection.cursor()

        table_username = (request.form.get("name",) or "").strip()
        table_password = (request.form.get("password") or "").strip()

        sql = "SELECT * FROM users WHERE name = ? AND password = ?"
        cursor.execute(sql, (table_username, table_password))

        result = cursor.fetchone()
        print("Entered username:", table_username)
        print("Entered password:", table_password)
        print("Result:", result)

        if result:
            print("Login successful!")
            return render_template("homepage.html")
        else:
            print("Invalid username or password!")

        connection.close()

    return render_template("login.html")

@app.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    if request.method == "POST":
        connection = sqlite3.connect('test.db')
        cursor = connection.cursor()

        table_email = request.form.get("email")
        sql = "SELECT * FROM users WHERE email = ?"
        cursor.execute(sql, (table_email,))
        result = cursor.fetchone()
        print("Entered username:", table_email)

        
        if result:
            print("Resetting")
            session["reset_email"] = table_email
            return render_template("change-pass.html")

        else:
            print("Email does not exist")

        connection.close()

    return render_template("email-check.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    if request.method == "POST":

        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        # Check that passwords match
        if new_password != confirm_password:
            return "Passwords do not match"

        # Get the email from the previous verification step
        email = session.get("reset_email")
        print("New password:", new_password)
        print("Email:", email)
        if not email:
            return "Email verification required"

        connection = sqlite3.connect("test.db")
        cursor = connection.cursor()

        # Update the password belonging to that email
        cursor.execute(
            "UPDATE users SET password = ? WHERE email = ?",
            (new_password, email)
        )

        connection.commit()

        connection.close()

        # Remove the email after the password has been changed
        session.pop("reset_email", None)

        return redirect("/login")

    return render_template("change-pass.html")


if __name__ == "__main__":
    app.run(debug=True)