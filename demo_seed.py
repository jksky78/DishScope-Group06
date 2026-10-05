"""
Creates demo accounts for DishScope so a tester can log in
without registering or waiting for an OTP email.

Run once from the project folder (the one containing main.py):
    python seed_demo.py

Safe to run more than once: existing demo accounts are not duplicated.
"""
import os
import sqlite3

from werkzeug.security import generate_password_hash

# main.py opens "test.db" and "dish_database.db" relative to the current
# folder, so work from the folder this script lives in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

USERS_DB = "test.db"
DISH_DB = "dish_database.db"

DEMO_STUDENT = ("demo_student", "student@example.com", "Student123!", "student")
DEMO_VENDOR = ("demo_vendor", "vendor@example.com", "Vendor123!", "vendor")


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

    add_user(users, *DEMO_STUDENT)
    vendor_id = add_user(users, *DEMO_VENDOR)

    # Every vendor needs a vendors row with the same id as their users row
    if not users.execute("SELECT 1 FROM vendors WHERE id = ?", (vendor_id,)).fetchone():
        users.execute(
            "INSERT INTO vendors (ID, name, vendor_name, vendor_location, role) "
            "VALUES (?, ?, ?, ?, ?)",
            (vendor_id, DEMO_VENDOR[0], "Demo Kitchen", "Block A Cafeteria", "vendor"),
        )

    users.commit()
    users.close()

    print("Demo accounts ready.")
    print(f"  Student login: {DEMO_STUDENT[1]} / {DEMO_STUDENT[2]}")
    print(f"  Vendor login:  {DEMO_VENDOR[1]} / {DEMO_VENDOR[2]}")


if __name__ == "__main__":
    main()
