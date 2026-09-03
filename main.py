from flask import Flask, render_template, request, redirect, url_for
import sqlite3


app = Flask(__name__)

@app.get("/")
def home ():
    if request.method == 'GET':
        return render_template("homepage.html")

@app.route("/register", methods=["GET", "POST"])
def create_table():
    name = ""
    errors = []
    if request.method == "POST":
        connection = sqlite3.connect('test.db')
        cursor = connection.cursor()
        table2 = 'drop table users'
        table = '''create table if not exists users(
                ID integer primary key autoincrement,
                name text not null,
                password text not null,
                email text not null
        )'''
        input_insert = "insert into users(name, password, email) values(?, ?, ?)"
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        table_username = request.form.get("name")
        table_password = (request.form.get("password",) or "").strip()
        table_email = request.form.get("email")
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
            cursor.execute(input_insert, (name, password, email))
            connection.commit()
            connection.close()
            return f'Hello, {name}'

    return render_template('register.html')
    


if __name__ == "__main__":
    app.run(debug=True)