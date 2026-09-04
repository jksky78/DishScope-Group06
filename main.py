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
    


if __name__ == "__main__":
    app.run(debug=True)