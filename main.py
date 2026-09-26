from flask import Flask, render_template, request, redirect, url_for, session , flash
from itsdangerous import URLSafeSerializer
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3


app = Flask(__name__)
app.secret_key = "DishScope-000"

@app.get("/")
def home ():
    if request.method == 'GET':
        print(session)
        return render_template("homepage.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    name = ""
    errors = []
    if request.method == "POST":
        print(">>> SUCCESS: The register POST route was hit! <<<")
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
        hashed_password = generate_password_hash(password)
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
            cursor.execute(input_insert, (table_username, hashed_password, email, role))
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
        table_email = request.form.get("email")
        sql = "SELECT id, name, password_hash, role FROM users WHERE name = ?"
        cursor.execute(sql, (table_username,))
        result = cursor.fetchone()
        print("Entered username:", table_username)
        print("Entered password:", table_password)
        print("Result:", result)

        
        if result and check_password_hash(result[2], table_password):
            print("Login successful!")   
            session["logged_in"] = True
            session["user"] = result[1]
            session['user_id'] = result[0]     
            session['role'] = 'student'
            print("SESSION:", session)         
            return redirect(url_for('dish_view'))
        else:
            print("Invalid username or password!")
            return render_template('login.html', error="Invalid username or password!")
        
    return render_template("login.html")

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for('home'))


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

@app.route("/add_dish", methods=["GET", "POST"])
def add_dish():
    return render_template("dish-registration.html")


@app.route("/create_dish", methods=["GET", "POST"])
def create_dish():
  if request.method == "POST":
    conn = sqlite3.connect("dish_database.db")
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS dishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price REAL,
                description TEXT,
                calories INTEGER,
                ingredients TEXT,
                vegetarian TEXT,
                spicy_level TEXT,
                allergens TEXT,
                availability TEXT,
                image_filename TEXT
            )
        """)
    input_insert_dish = "insert into dishes (name, category, price, description, calories, ingredients, vegetarian, spicy_level, allergens, availability, image_filename) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    name = request.form.get("name")
    category = request.form.get("category")
    price = request.form.get("price")
    description = request.form.get("description")
    calories = request.form.get("calories")
    ingredients = request.form.get("ingredients")
    vegetarian = request.form.get("vegetarian")
    spicy_level = request.form.get("spicy_level")
    allergens = request.form.get("allergens")
    availability = request.form.get("availability")

    # Handle image filename if uploaded
    image_filename = ""
    if "image" in request.files:
        file = request.files["image"]
        if file.filename != "":
            image_filename = file.filename
    cursor.execute(input_insert_dish, (name, category, price, description, calories, ingredients, vegetarian, spicy_level, allergens, availability, image_filename))
    conn.commit()
    conn = sqlite3.connect("dish_database.db")
    conn.row_factory = (
      sqlite3.Row
  ) 
    cursor = conn.cursor()

  # Fetch all dishes from the table
    cursor.execute("SELECT * FROM dishes")
    dishes = cursor.fetchall()  # Grab all rows

  # Close the connection
    conn.close()
    return render_template("dishpage.html", dishes=dishes)
  
def get_dish_from_db():
  # Connect to SQLite database
  conn = sqlite3.connect("dish_database.db")
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  # Fetch the first dish
  cursor.execute("SELECT * FROM dishes WHERE id = 1")
  dish = cursor.fetchone()
  conn.close()
  return dish


@app.route("/dish_view", methods=["GET", "POST"])
def dish_view():
    if "logged_in" in  session:
        print(session)
        conn = sqlite3.connect("dish_database.db")
        conn.row_factory = (sqlite3.Row) 
        cursor = conn.cursor()
        try:
        # Try to fetch all dishes from the table
            cursor.execute("SELECT * FROM dishes")
            dishes = cursor.fetchall()  # Grab all rows
        except sqlite3.OperationalError:
        # If the table doesn't exist yet, set dishes to an empty list
            dishes = []
    else:
        print("You dont have access to this page")
        flash('You must be logged in to view that page.', 'danger')
        return redirect(url_for('home', error="You do not have access to this page, please log in"))
        

    conn.close()
    return render_template("dishpage.html", dishes=dishes)

if __name__ == "__main__":
    app.run(debug=True)