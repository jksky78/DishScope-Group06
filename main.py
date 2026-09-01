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
    if request.method == "POST":
        connection = sqlite3.connect('test.db')
        cursor = connection.cursor()
        table2 = 'drop table users'
        table = '''create table if not exists users(
                ID integer primary key autoincrement,
                name text,
                password text
        )'''
        input_insert = "insert into users(name, password) values(?, ?)"
        name = request.form['name']
        cursor.execute(table)
        cursor.execute(input_insert, (name, "random"))
        connection.commit()
        connection.close()
        return f'Hello, {name}'
    return render_template('register.html')
    


if __name__ == "__main__":
    app.run(debug=True)