"""
Creates demo accounts and sample data for DishScope so a tester can log in
without registering or waiting for an OTP email.

Run once from the project folder (the one containing main.py):
    python seed_demo.py

Safe to run more than once: existing demo data is not duplicated.
"""
import os
import sqlite3
from datetime import datetime, timezone, timedelta

from werkzeug.security import generate_password_hash


os.chdir(os.path.dirname(os.path.abspath(__file__)))

USERS_DB = "test.db"
DISH_DB = "dish_database.db"

# Demo account with password
DEMO_STUDENT = ("demo_student", "student@example.com", "Student123!", "student")
DEMO_VENDOR = ("demo_vendor", "vendor@example.com", "Vendor123!", "vendor")

SAMPLE_DISHES = [

    ("Nasi Lemak", "Rice", 6.50, "Coconut rice with sambal, egg and anchovies.",
     650, "Rice, coconut milk, anchovies, egg, sambal", "No", "Medium", "Egg, Fish", "Yes"),
    ("Vegetable Fried Rice", "Rice", 5.50, "Wok-fried rice with mixed vegetables.",
     520, "Rice, carrot, peas, cabbage, soy sauce", "Yes", "Mild", "Soy", "Yes"),
    ("Chicken Laksa", "Noodles", 8.00, "Spicy coconut curry noodle soup with chicken.",
     720, "Rice noodles, chicken, coconut milk, chilli", "No", "Hot", "Shellfish", "No"),
]

SAMPLE_REVIEWS = [
    (5, "Really tasty and filling. Great value!"),
    (4, "Good flavour, a little spicy for me."),
]


def create_tables():
    """Same schema as init_db / init_dish_db / init_dish_review in main.py."""
    conn = sqlite3.connect(USERS_DB)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            ID integer primary key autoincrement,
            name text not null,
            password text not null,
            email text not null,
            role text not null
        );
        CREATE TABLE IF NOT EXISTS vendors (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            vendor_name TEXT NOT NULL,
            vendor_location TEXT NOT NULL,
            role TEXT NOT NULL
        );
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
        );
        CREATE TABLE IF NOT EXISTS password_resets (
            email      TEXT PRIMARY KEY,
            otp_hash   TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            attempts   INTEGER DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect(DISH_DB)
    conn.executescript("""
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
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dish_id INTEGER,
            user_id INTEGER,
            student_name TEXT,
            rating INTEGER,
            comment TEXT,
            date_posted TEXT
        );
    """)
    conn.commit()
    conn.close()


def add_user(conn, name, email, password, role):
    """Insert a user unless the email already exists. Returns the user id."""
    row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        (name, email, generate_password_hash(password), role),
    )
    return cur.lastrowid


def main():
    create_tables()

    users = sqlite3.connect(USERS_DB)
    dishes = sqlite3.connect(DISH_DB)

    student_id = add_user(users, *DEMO_STUDENT)
    vendor_id = add_user(users, *DEMO_VENDOR)

    # Every vendor needs a vendors row with the same id as their users row
    if not users.execute("SELECT 1 FROM vendors WHERE id = ?", (vendor_id,)).fetchone():
        users.execute(
            "INSERT INTO vendors (ID, name, vendor_name, vendor_location, role) "
            "VALUES (?, ?, ?, ?, ?)",
            (vendor_id, DEMO_VENDOR[0], "Demo Kitchen", "Block A Cafeteria", "vendor"),
        )

    # Sample dishes and reviews (only if this vendor has no dishes yet)
    if not dishes.execute(
        "SELECT 1 FROM dishes WHERE vendor_id = ?", (vendor_id,)
    ).fetchone():
        for d in SAMPLE_DISHES:
            dishes.execute(
                "INSERT INTO dishes (vendor_id, name, category, price, description, "
                "calories, ingredients, vegetarian, spicy_level, allergens, "
                "availability, image_filename) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '')",
                (vendor_id, *d),
            )

        first_dish_id = dishes.execute(
            "SELECT id FROM dishes WHERE vendor_id = ? ORDER BY id LIMIT 1",
            (vendor_id,),
        ).fetchone()[0]
        now = datetime.now(timezone(timedelta(hours=8)))
        for i, (rating, comment) in enumerate(SAMPLE_REVIEWS):
            posted = (now - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")
            dishes.execute(
                "INSERT INTO reviews (dish_id, user_id, student_name, rating, comment, date_posted) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (first_dish_id, student_id, DEMO_STUDENT[0], rating, comment, posted),
            )

    users.commit()
    dishes.commit()
    users.close()
    dishes.close()

    print("Demo data ready.")
    print(f"  Student login: {DEMO_STUDENT[1]} / {DEMO_STUDENT[2]}")
    print(f"  Vendor login:  {DEMO_VENDOR[1]} / {DEMO_VENDOR[2]}")


if __name__ == "__main__":
    main()