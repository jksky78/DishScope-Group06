
from flask import Flask, render_template, request, redirect, url_for, session , flash, jsonify
from itsdangerous import URLSafeSerializer
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
from email.message import EmailMessage
import os, hmac, hashlib, secrets, smtplib, sqlite3, random, time
import uuid
from datetime import datetime, timezone, timedelta
import sqlite3

def load_env():
    try:
        with open(".env", "r") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

    except FileNotFoundError:
        print(".env file not found")

load_env()
app = Flask(__name__)
app.secret_key = "DishScope-000"
OTP_VALID_MINUTES = 10
OTP_MAX_ATTEMPTS = 5
TIME_FMT = "%Y-%m-%d %H:%M:%S"
UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


def flash_once(message, category="message"):
    session.pop('_flashes', None)
    flash(message, category)

@app.before_request
def require_login():
    print("CURRENT ENDPOINT:", request.endpoint)
    # Route endpoints that anyone is allowed to visit without logging in
    public_endpoints = ['login', 'register', 'static', 'home', 'verify_email','reset_password', 'verify_otp',
                        'verify_reset_otp' ] 
    # Routes that ONLY vendors are allowed to access
    vendor_endpoints = ['add_dish', 'edit_dish', 'menu_management', 'report summary']
    # If the current request endpoint requires login and user session is missing
    if request.endpoint and request.endpoint not in public_endpoints:
        if not session.get('logged_in'):
            flash_once('You must be logged in to view that page.', 'danger')
            return redirect(url_for('home', error="You do not have access to this page, please log in"))
    # 2. Check if the page requires vendor access, but the user is a student
    if request.endpoint in vendor_endpoints and session.get('role') != 'vendor':
        flash_once('Access denied. You must be logged in as a vendor to access this page.', 'danger')
        return redirect(url_for('home'))
@app.get("/")
def home ():
    if request.method == 'GET':
        print(session)
        return render_template("homepage.html")
def init_db():
    # connects to  database (and creates the file if it doesn't exist yet)
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # CREATE TABLE IF NOT EXISTS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
               ID integer primary key autoincrement,
                name text not null,
                password text not null,
                email text not null,
                role text not null
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            vendor_name TEXT NOT NULL,
            vendor_location TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_registrations (
            email         TEXT PRIMARY KEY,
            name          TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT,
            vendor_name   TEXT,
            vendor_location   TEXT,
            otp_hash      TEXT NOT NULL,
            expires_at    TEXT NOT NULL,
            attempts      INTEGER DEFAULT 0,
            last_sent     TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            email      TEXT PRIMARY KEY,
            otp_hash   TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            attempts   INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
def init_dish_db():
    # connects to  database (and creates the file if it doesn't exist yet)
    conn = sqlite3.connect('dish_database.db')
    cursor = conn.cursor()
    
    # CREATE TABLE IF NOT EXISTS
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS dishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER,
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
    
    conn.commit()
    conn.close()
def init_dish_review():
    conn = sqlite3.connect("dish_database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dish_id INTEGER,      
        user_id INTEGER,       
        student_name TEXT,     
        rating INTEGER,        
        comment TEXT,          
        date_posted TEXT       
    )
""")
    conn.commit()
    conn.close()
init_db()
init_dish_db()
init_dish_review()

def generate_otp():
    return f"{secrets.randbelow(10**6):06d}" 

def hash_otp(otp):
    return hmac.new(app.secret_key.encode(), otp.encode(), hashlib.sha256).hexdigest()

def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg["Subject"] = "Your DishScope verification code"
    msg["From"] = os.environ["SMTP_EMAIL"]
    msg["To"] = to_email
    msg.set_content(
        f"Your DishScope verification code is: {otp}\n\n"
        f"It expires in {OTP_VALID_MINUTES} minutes. "
        f"If you didn't request this, you can ignore this email."
    )
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["SMTP_EMAIL"], os.environ["SMTP_APP_PASSWORD"])
        smtp.send_message(msg) 



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        role = request.form.get("role", "student")

        conn = sqlite3.connect("test.db")
        taken = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
        if taken:
            conn.close()
            flash_once("That email is already registered.", "danger")
            return redirect(url_for("register"))

        otp = generate_otp()
        now = datetime.now()
        conn.execute("""
            INSERT OR REPLACE INTO pending_registrations
            (email, name, password_hash, role, vendor_name, vendor_location,
             otp_hash, expires_at, attempts, last_sent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (
            email, name, generate_password_hash(request.form["password"]), role,
            request.form.get("vendor_name", "").strip(),
            request.form.get("vendor_location", "").strip(),
            hash_otp(otp),
            (now + timedelta(minutes=OTP_VALID_MINUTES)).strftime(TIME_FMT),
            now.strftime(TIME_FMT),
        ))
        conn.commit()
        conn.close()

        try:
            send_otp_email(email, otp)
        except Exception as e:
            print("Email failed:", e)
            flash_once("Could not send the verification email.", "danger")
            return redirect(url_for("register"))

        session["pending_email"] = email          # <-- this is what verify_otp looks for
        return redirect(url_for("verify_otp"))

    return render_template("register.html")

    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        
        connection = sqlite3.connect('test.db')
        cursor = connection.cursor()
        table_username_email = (request.form.get("name",) or "").strip()
        table_password = (request.form.get("password") or "").strip()
        sql = "SELECT id, name, password, role FROM users WHERE name = ? OR email = ?"
        cursor.execute(sql, (table_username_email, table_username_email))
        result = cursor.fetchone()
        print("Entered username or email:", table_username_email)
        print("Entered password:", table_password)
        print("Result:", result)
        
        
        if result and check_password_hash(result[2], table_password):
            print("Login successful!")   
            session["logged_in"] = True
            session["user"] = result[1]
            session['user_id'] = result[0] 
            if result[3] == "student":    
                session['role'] = 'student'
            else:
                session['role'] = 'vendor'
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
        email = request.form.get("email", "").strip().lower()

        conn = sqlite3.connect("test.db")
        user = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()

        if not user:
            conn.close()
            flash_once("Email not found in our system. Please check and try again.", "danger")
            return redirect(url_for("verify_email"))

        otp = generate_otp()
        expires = (datetime.now() + timedelta(minutes=OTP_VALID_MINUTES)).strftime(TIME_FMT)
        conn.execute(
            "INSERT OR REPLACE INTO password_resets (email, otp_hash, expires_at, attempts) "
            "VALUES (?, ?, ?, 0)",
            (email, hash_otp(otp), expires),
        )
        conn.commit()
        conn.close()

        try:
            send_otp_email(email, otp)
        except Exception as e:
            print("Email failed:", e)
            flash_once("Could not send the email. Try again later.", "danger")
            return redirect(url_for("verify_email"))

        session["reset_email"] = email
        session["reset_verified"] = False
        return redirect(url_for("verify_reset_otp"))

    return render_template("email-check.html")

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    email = session.get("pending_email")
    if not email:
        return redirect(url_for("register"))
    # (delete the user_id = session.get('user_id') line)

    if request.method == "POST":
        entered = request.form.get("otp", "").strip()
        conn = sqlite3.connect("test.db")
        conn.row_factory = sqlite3.Row  
        pending = conn.execute(
            "SELECT * FROM pending_registrations WHERE email = ?", (email,)
        ).fetchone()

        if not pending:
            conn.close()
            flash_once("Session expired. Please register again.", "danger")
            return redirect(url_for("register"))

        if datetime.now() > datetime.strptime(pending["expires_at"], TIME_FMT):
            conn.close()
            flash_once("Code expired. Please verify your email again", "danger")
            return redirect(url_for("verify_otp"))

        if pending["attempts"] >= OTP_MAX_ATTEMPTS:
            conn.execute("DELETE FROM pending_registrations WHERE email = ?", (email,))
            conn.commit()
            conn.close()
            session.pop("pending_email", None)
            flash_once("Too many wrong attempts. Please register again.", "danger")
            return redirect(url_for("register"))

        if not hmac.compare_digest(pending["otp_hash"], hash_otp(entered)):
            conn.execute(
                "UPDATE pending_registrations SET attempts = attempts + 1 WHERE email = ?",
                (email,),
            )
            conn.commit()
            conn.close()
            flash_once("Incorrect code.", "danger")
            return redirect(url_for("verify_otp"))

        # Correct code: create the real account
        try:
            cur = conn.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (pending["name"], email, pending["password_hash"], pending["role"]),
            )
            new_user_id = cur.lastrowid

            if pending["role"] == "vendor":
                # ...CREATE TABLE stays the same...
                conn.execute(
                    "INSERT INTO vendors (ID, name, vendor_name, vendor_location, role) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (new_user_id, pending["name"], pending["vendor_name"],
                     pending["vendor_location"], pending["role"]),
                )
        except sqlite3.IntegrityError:
            pass
        conn.execute("DELETE FROM pending_registrations WHERE email = ?", (email,))
        conn.commit()
        conn.close()

        session.pop("pending_email", None)
        flash_once("Email verified! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("verification-otp.html", email=email,
                           form_action=url_for("verify_otp"))

@app.route("/verify_reset_otp", methods=["GET", "POST"])
def verify_reset_otp():
    email = session.get("reset_email")
    if not email:
        return redirect(url_for("verify_email"))

    if request.method == "POST":
        entered = request.form.get("otp", "").strip()

        conn = sqlite3.connect("test.db")
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM password_resets WHERE email = ?", (email,)
        ).fetchone()

        if not row or datetime.now() > datetime.strptime(row["expires_at"], TIME_FMT):
            conn.close()
            flash_once("Code expired. Please request a new one.", "danger")
            return redirect(url_for("verify_email"))

        if row["attempts"] >= OTP_MAX_ATTEMPTS:
            conn.execute("DELETE FROM password_resets WHERE email = ?", (email,))
            conn.commit()
            conn.close()
            session.pop("reset_email", None)
            flash_once("Too many wrong attempts. Please start again.", "danger")
            return redirect(url_for("verify_email"))

        if not hmac.compare_digest(row["otp_hash"], hash_otp(entered)):
            conn.execute(
                "UPDATE password_resets SET attempts = attempts + 1 WHERE email = ?", (email,)
            )
            conn.commit()
            conn.close()
            flash_once("Incorrect code.", "danger")
            return redirect(url_for("verify_reset_otp"))

        # Correct code
        conn.execute("DELETE FROM password_resets WHERE email = ?", (email,))
        conn.commit()
        conn.close()

        session["reset_verified"] = True
        return render_template("change-pass.html")

    return render_template("verification-otp.html", email=email,
                           form_action=url_for("verify_reset_otp"))
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if not session.get("reset_verified") or not session.get("reset_email"):
        flash_once("Please verify your email first.", "danger")
        return redirect(url_for("verify_email"))
    if request.method == "POST":
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        # Check that passwords match
        if not new_password or new_password != confirm_password:
            flash_once("Passwords do not match.", "danger")
            return redirect(url_for("reset_password"))
        # Get the email from the previous verification step
        email = session.get("reset_email")
        print("New password:", new_password)
        print("Email:", email)
        if not email:
            return "Email verification required"
        hashed_password = generate_password_hash(new_password)
        connection = sqlite3.connect("test.db")
        cursor = connection.cursor()
        # Update the password belonging to that email
        cursor.execute(
            "UPDATE users SET password = ? WHERE email = ?",
            (hashed_password, email)
        )
        connection.commit()
        connection.close()
        # Remove the email after the password has been changed
        session.pop("reset_email", None)
        session.pop("reset_verified", None)
        flash_once("Password updated. You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("change-pass.html")
@app.route("/add_dish", methods=["GET", "POST"])
def add_dish():
    return render_template("dish-registration.html")
@app.route("/upload-image", methods=["POST"])
def upload():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        return jsonify({
            'message': 'Image uploaded successfully!', 
            'filename': filename
        }), 200
        
    
@app.route("/create_dish", methods=["GET", "POST"])
def create_dish():
  if request.method == "POST":
    user_id = session.get('user_id')
    # 2. Connect to users database ('test.db') and fetch user
    conn_users = sqlite3.connect("test.db")
    conn_users.row_factory = sqlite3.Row
    cursor_users = conn_users.cursor()
    user = cursor_users.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn_users.close()  # Close when done
    conn = sqlite3.connect("dish_database.db")
    file = request.files['file']
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS dishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER,
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
    input_insert_dish = "insert into dishes (vendor_id, name, category, price, description, calories, ingredients, vegetarian, spicy_level, allergens, availability, image_filename) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
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
    cursor.execute(input_insert_dish, (user_id, name, category, price, description, calories, ingredients, vegetarian, spicy_level, allergens, availability, unique_filename))
    print(unique_filename)
    conn.commit()
    conn.close()
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
    return render_template("dishpage.html", dishes=dishes, user=user)
  
  
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
        # 1. Get user_id from session FIRST
        user_id = session.get('user_id')
    
    # 2. Connect to users database ('test.db') and fetch user
        conn_users = sqlite3.connect("test.db")
        conn_users.row_factory = sqlite3.Row
        cursor_users = conn_users.cursor()
    
        user = cursor_users.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn_users.close()  # Close when done
        conn = sqlite3.connect("dish_database.db")
        conn.row_factory = (sqlite3.Row) 
        cursor = conn.cursor()
        try:
        # Try to fetch all dishes from the table
            cursor.execute("""
                SELECT dishes.*, COALESCE(AVG(reviews.rating), 0) AS avg_rating
                FROM dishes 
                LEFT JOIN reviews ON dishes.id = reviews.dish_id 
                GROUP BY dishes.id
            """)
            dishes = cursor.fetchall() # Grab all rows
            print("ALL DISHES FOUND:", dishes)
        except sqlite3.OperationalError:
            print("DATABASE ERROR:")
        # If the table doesn't exist yet, set dishes to an empty list
            dishes = []
        if dishes:
            print(dishes[0]['image_filename'])
        
        return render_template("dishpage.html", dishes=dishes, user=user)
    else:
        print("You dont have access to this page")
        flash_once('You must be logged in to view that page.', 'danger')
        return redirect(url_for('home', error="You do not have access to this page, please log in"))
        
@app.errorhandler(413)
def too_large(e):
    # Flash a friendly message (requires a secret_key set on your app)
    return render_template('dish-registration.html', error="The uploaded image is too large! Please choose an image under 5MB."), 413

@app.route("/menu management", methods=["GET", "POST"])
def menu_management():
        conn = sqlite3.connect("test.db")
        conn.row_factory = (sqlite3.Row)
        cursor = conn.cursor()
        user_id = session.get('user_id')
        user = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        # Connect dish database next
        conn = sqlite3.connect("dish_database.db")
        conn.row_factory = (sqlite3.Row) 
        cursor = conn.cursor()
        dishes = cursor.execute("SELECT * FROM dishes WHERE vendor_id = ?", (user_id,)).fetchall()
        total_dishes = cursor.execute("SELECT COUNT(*) FROM dishes WHERE vendor_id = ?", (user_id,)).fetchone()[0]
        total_availability = cursor.execute("SELECT COUNT(*) FROM dishes WHERE vendor_id = ? AND availability = 'Yes' COLLATE NOCASE", (user_id,)).fetchone()[0]
        total_unavailability = cursor.execute("SELECT COUNT(*) FROM dishes WHERE vendor_id = ? AND availability = 'No' COLLATE NOCASE", (user_id,)).fetchone()[0]
        
        
        
        return render_template("menu management.html", user=user, dishes=dishes, total_dishes=total_dishes,
                               total_availability=total_availability, total_unavailability=total_unavailability)

@app.route("/dish/<int:dish_id>", methods=["GET", "POST"])
def dish_detail(dish_id):
        print(f"Clicked Dish ID: {dish_id}")
    
        conn = sqlite3.connect("dish_database.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
    
        # Fetch specific dish info using the passed IDs
        dish = cursor.execute('SELECT * FROM dishes WHERE id = ?', (dish_id,)).fetchone()
        reviews = cursor.execute('SELECT * FROM reviews WHERE dish_id = ? ORDER BY id DESC', (dish_id,)).fetchall()
        # 3. Calculate total reviews and average rating using SQLite built-in functions
        stats = cursor.execute('''
            SELECT COUNT(*) as total, AVG(rating) as average 
            FROM reviews WHERE dish_id = ?
        ''', (dish_id,)).fetchone()
    
        total_reviews = stats['total'] if stats['total'] else 0
        # Round average to 1 decimal place (e.g., 3.3), default to 0 if no reviews
        avg_rating = round(stats['average'], 1) if stats['average'] else 0.0
        conn.close()
        # 2. Connect to users/vendors database (test.db) using the dish's vendor_id
        conn_users = sqlite3.connect("test.db")
        conn_users.row_factory = sqlite3.Row
        cursor_users = conn_users.cursor()
        
        vendor = None
        if dish and dish['vendor_id']:
            vendor = cursor_users.execute('SELECT vendor_name FROM vendors WHERE id = ?', (dish['vendor_id'],)).fetchone()
    
        conn_users.close()
    # Ratings filter
        rating_filter = request.args.get('rating', 'all')
        sort = request.args.get('sort', 'recent')
    # whitelist ORDER BY options
        order_options = {
            'recent':  'date_posted DESC',
            'oldest':  'date_posted ASC',
            'highest': 'rating DESC, date_posted DESC',
            'lowest':  'rating ASC, date_posted DESC',
        }
        order_by = order_options.get(sort, order_options['recent'])
        query = "SELECT * FROM reviews WHERE dish_id = ?"
        params = [dish_id]
        if rating_filter in ('1', '2', '3', '4', '5'):
            query += " AND rating = ?"
            params.append(int(rating_filter))
        query += " ORDER BY " + order_by
        conn = sqlite3.connect("dish_database.db")
        conn.row_factory = sqlite3.Row
        reviews = conn.execute(query, params).fetchall()
    # Summary stats must come from ALL reviews, not the filtered list
        stats = conn.execute(
            "SELECT ROUND(AVG(rating), 1) AS avg_rating, COUNT(*) AS total "
            "FROM reviews WHERE dish_id = ?", (dish_id,)
        ).fetchone()
        similar_dishes = conn.execute("""
        SELECT id, name, category, price, vegetarian, spicy_level, image_filename
        FROM dishes
        WHERE category = ?
          AND id != ?
        ORDER BY
            (vegetarian = ?) DESC,
            ABS(CAST(price AS REAL) - ?) ASC
        LIMIT 4
    """, (
        dish['category'],
        dish['id'],
        dish['vegetarian'],
        float(dish['price'])
    )).fetchall()
        conn.close()
        
        return render_template("dish detailed dashboard.html", dish=dish, vendor=vendor, reviews=reviews, 
                               total_reviews=total_reviews, avg_rating=avg_rating, rating_filter=rating_filter, sort=sort,
                               similar_dishes=similar_dishes)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    conn = sqlite3.connect("test.db")
    conn.row_factory = (sqlite3.Row)
    cursor = conn.cursor()
    user_id = session.get('user_id')
    # HANDLE POST (When user clicks Save/Submit)
    if request.method == "POST":
        new_name = request.form.get('name')
    
        if session.get('role') == 'student':
        # Update user table only
            cursor.execute('UPDATE users SET name = ? WHERE id = ?', (new_name, user_id))
        
        elif session.get('role') == 'vendor':
            print("if reached")
            new_vendor_name = request.form.get('vendor_name')
            new_vendor_location = request.form.get('vendor_location')
            cursor.execute('UPDATE users SET name = ? WHERE id = ?', (new_name, user_id))
            cursor.execute('UPDATE vendors SET name = ?, vendor_name = ?, vendor_location = ? WHERE id = ?', 
                       (new_name, new_vendor_name, new_vendor_location, user_id))
        
   
        conn.commit()
        conn.close()
        
        # Refresh the page 
        flash_once("Profile updated successfully!", "success")
        return redirect(url_for('profile'))
    user = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    print(session['user_id'])
    if session['role'] == "vendor":
        vendor = cursor.execute('SELECT * FROM vendors WHERE id = ?', (user_id,)).fetchone()
    else:
        vendor = None
    return render_template('profile.html', user=user, vendor=vendor)
@app.route("/dish/<int:dish_id>/review", methods=["GET", "POST"])
def add_review(dish_id):
    print("ALL FORM DATA:", request.form)
    user_id = session.get('user_id')
    rating = request.form.get('rating') 
    comment = request.form.get('comment')
 
    if not rating:
        print("failed: no rating selected")
        flash_once("Please select a star rating!", "danger")
        return redirect(url_for('dish_detail', dish_id=dish_id))
    
    rating_int = int(rating)
    
    # Fetch student name from test.db
    conn_users = sqlite3.connect("test.db")
    conn_users.row_factory = sqlite3.Row
    cursor_users = conn_users.cursor()
    student = cursor_users.execute('SELECT name FROM users WHERE id = ?', (user_id,)).fetchone()
    conn_users.close()
    
    student_name = student['name'] if student else "Anonymous"
    
    # Save review into dish_database.db
    malaysia_time = timezone(timedelta(hours=8))
    date_post = datetime.now(malaysia_time).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("dish_database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reviews (dish_id, user_id, student_name, rating, comment, date_posted)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dish_id, user_id, student_name, rating_int, comment, date_post))
    
    conn.commit()
    conn.close()
    print("SUCCESS: Review saved to database")
    
    flash_once("Review added successfully!", "success")
    return redirect(url_for('dish_detail', dish_id=dish_id))
@app.route('/delete_dish/<int:dish_id>', methods=['POST'])
def delete_dish(dish_id):
    # Check the specific vendor with id
    conn = sqlite3.connect("test.db")
    conn.row_factory = (sqlite3.Row)
    cursor = conn.cursor()
    user_id = session.get('user_id')
    conn.close()
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session.get('user_id')
    # Connect to the dish database
    conn = sqlite3.connect("dish_database.db")
    cursor = conn.cursor()
     # Delete the selected dish created by the specific vendor
    cursor.execute("DELETE FROM dishes WHERE id = ? AND vendor_id = ?", (dish_id, user_id))
    
    conn.commit()
    conn.close()
    # Redirect back to the menu management page
    return redirect(url_for('menu_management')) 
@app.route('/dish/<int:dish_id>/edit', methods=['GET', 'POST'])
def edit_dish(dish_id):
    conn = sqlite3.connect("test.db")
    conn.row_factory = (sqlite3.Row)
    cursor = conn.cursor()
    user_id = session.get('user_id')
    conn.close()
    conn = sqlite3.connect("dish_database.db")
    conn.row_factory = (sqlite3.Row)
    cursor = conn.cursor()
    if request.method == 'POST':
            # 1. Grab all text/dropdown inputs from the form
            name = request.form.get('name')
            category = request.form.get('category')
            price = request.form.get('price')
            spicy_level = request.form.get('spicy_level')
            calories = request.form.get('calories')
            ingredients = request.form.get('ingredients')
            allergens = request.form.get('allergens')
            is_available = request.form.get('availability')
            description = request.form.get('description')
            # 2. Check if a new image file was uploaded
            file = request.files['file']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
    
    
                # 3. UPDATE including the new image filename
                cursor.execute('''
                    UPDATE dishes 
                    SET name = ?, category = ?, price = ?, spicy_level = ?, 
                        allergens = ?, availability = ?, image_filename = ?, calories = ?,
                        ingredients = ?, description = ?
                    WHERE id = ? AND vendor_id = ?
                ''', (name, category, price, spicy_level, allergens, is_available, unique_filename, calories, ingredients, description, dish_id, user_id))
                dish = cursor.execute("SELECT * FROM dishes where id = ? AND vendor_id = ?", (dish_id, user_id)).fetchone()
            else:
                # 4. UPDATE WITHOUT touching the image column (keeps the existing image safe if no new one was chosen)
                cursor.execute('''
                    UPDATE dishes 
                    SET name = ?, category = ?, price = ?, spicy_level = ?, 
                        allergens = ?, availability = ?, calories = ?, ingredients = ?, description = ?
                    WHERE id = ? AND vendor_id = ?
                ''', (name, category, price, spicy_level, allergens, is_available, calories, ingredients, description, dish_id, user_id))
                dish = cursor.execute("SELECT * FROM dishes where id = ? AND vendor_id = ?", (dish_id, user_id)).fetchone()
            conn.commit()
            conn.close()
    
            flash_once("Dish updated successfully!", "success")
            return redirect(url_for('edit_dish', dish_id=dish_id))
    dish = cursor.execute("SELECT * FROM dishes WHERE id = ? AND vendor_id = ?", (dish_id, user_id)).fetchone()
    conn.close()
    return render_template("edit_dish.html", dish=dish)
@app.route('/report_summary', methods=['POST', 'GET'])
def report_summary():
    conn = sqlite3.connect("test.db")
    conn.row_factory = (sqlite3.Row)
    cursor = conn.cursor()
    user_id = session.get('user_id')
    vendor = cursor.execute('SELECT * FROM vendors WHERE id = ?', (user_id,)).fetchone()
    conn.close()
        # Connect dish database next
    conn = sqlite3.connect("dish_database.db")
    conn.row_factory = (sqlite3.Row) 
    cursor = conn.cursor()
    
    total_dishes = cursor.execute("SELECT COUNT(*) FROM dishes WHERE vendor_id = ?", (user_id,)).fetchone()[0]
    # Total review on the dish
    total_reviews = cursor.execute("""
        SELECT COUNT(reviews.id) AS total_reviews 
        FROM reviews 
        JOIN dishes ON reviews.dish_id = dishes.id 
        WHERE dishes.vendor_id = ?
    """, (user_id,)).fetchone()['total_reviews']
    # Highest rated dish
    highest_rated = cursor.execute("""
        SELECT dishes.name, dishes.image_filename, AVG(reviews.rating) AS avg_rating 
        FROM dishes 
        LEFT JOIN reviews ON dishes.id = reviews.dish_id 
        WHERE dishes.vendor_id = ? 
        GROUP BY dishes.id 
        ORDER BY avg_rating DESC 
        LIMIT 1
    """, (user_id,)).fetchone()
    most_reviewed = cursor.execute("""
        SELECT dishes.name, dishes.image_filename, COUNT(reviews.id) AS review_count 
        FROM dishes 
        LEFT JOIN reviews ON dishes.id = reviews.dish_id 
        WHERE dishes.vendor_id = ? 
        GROUP BY dishes.id 
        ORDER BY review_count DESC 
        LIMIT 1
    """, (user_id,)).fetchone()
    return render_template("report summary.html", vendor=vendor, total_dishes=total_dishes,
                            total_reviews=total_reviews, highest_rated=highest_rated, most_reviewed=most_reviewed)




if __name__ == "__main__":
    app.run(debug=True)
