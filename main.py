from flask import Flask, render_template, request, redirect, url_for
import sqlite3


app = Flask(__name__)

@app.get("/")
def home ():
    return render_template("homepage.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create-account-table")
def create_table():
    connection = sqlite3.connect("test.db")
    db_cursor = connection.cursor
    table_list = '''create table user(
        ID integer primary key autoincrement
        username, text
        email, text
         
    )'''

if __name__ == "__main__":
    app.run(debug=True)