# Gamer's History 🎮

## Overview
**Gamer's History** is a Flask-based web application that allows users to create and manage their personal video game libraries.  
The project was built as the final project for [CS50x](https://cs50.harvard.edu/x/).

With Gamer's History, users can:
- Import games from **Steam**.
- Manually add games to their collection.
- Upload and display **cover images** for each game.
- Track **hours played** and rate games.
- Switch between **list view** and **grid (tile) view** for better browsing.

The goal of the project is to provide an easy way for gamers to organize their collections and track their gaming history.

---

## Features
- **User Authentication**  
  Login and registration system (via username, not email).
- **Game Management**  
  Add, edit, and delete games from the library.
- **Cover Uploads**  
  Upload custom cover images to personalize the library.
- **Views**  
  Toggle between **list** and **grid** layouts.
- **Ratings & Playtime**  
  Record and display your rating and hours played for each game.
- **Multilingual Support**  
  Internationalization (English / Ukrainian).

---

## Technologies
- **Backend:** [Flask](https://flask.palletsprojects.com/) (Python)  
- **Database:** SQLite (via SQLAlchemy)  
- **Frontend:** HTML, CSS, Bootstrap  
- **Other:** Flask-Migrate, Flask-Login, Flask-Babel

---

1. Install dependencies  
   <details>
   <summary>Show instructions</summary>

   ```bash
   pip install -r requirements.txt
</details> 

2. Create and activate a virtual environment  
   <details>
   <summary>Show instructions</summary>

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/Mac
   venv\Scripts\activate      # On Windows
</details>

3. Install dependencies  
   <details>
   <summary>Show instructions</summary>

   ```bash
   pip install -r requirements.txt
</details>

4. Set environment variables  
   <details>
   <summary>Show instructions</summary>

   Example for Linux/Mac:
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
</details>

5. Initialize the database  
   <details>
   <summary>Show instructions</summary>

   ```bash
   flask db upgrade
</details>

6. Run the app  
   <details>
   <summary>Show instructions</summary>

   ```bash
   flask run
   Then open in your browser:
   http://127.0.0.1:5000
</details>

