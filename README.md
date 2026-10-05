# DishScope

A dish review web app where students can browse and review dishes,
and vendors can manage their menus.


## Setup

1. Create a virtual environment:
```
   python -m venv venv
```

2. Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Install packages:
```
    pip install -r requirements.txt
```

4. Create your `.env` file (this holds the email settings the app needs):

   a. Copy the template. In the project folder (next to `main.py`), run:
   - Windows: `copy .env.example .env`
   - Mac/Linux: `cp .env.example .env`

   b. Open the new `.env` file in a text editor and replace the placeholder values with your own:
```
   SMTP_EMAIL=your-gmail-address@gmail.com
   SMTP_APP_PASSWORD=your-16-character-app-password
   SECRET_KEY=any-long-random-string
   FLASK_DEBUG=1
```

   c. Save the file. Do not add quotes or spaces around `=`.

   Where to get the values:
   - `SMTP_EMAIL`: any Gmail address you own. It sends the verification codes.
   - `SMTP_APP_PASSWORD`: a Google App Password, not your normal password.
     Go to Google Account > Security, turn on 2-Step Verification, then search
     for "App passwords" and create one. Spaces in it are fine.
   - `SECRET_KEY`: any long random text, or generate one with
     `python -c "import secrets; print(secrets.token_hex(32))"`
   - `FLASK_DEBUG`: keep `1` for local testing.

   Note: without a valid Gmail and app password, the app still runs, but
   registration and password reset cannot send their verification emails.

5. Run the app:
```
   python main.py
```

6. Open http://127.0.0.1:5000 in your browser.
