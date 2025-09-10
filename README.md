# Gamer's History 🎮  

## Overview  
**Gamer's History** is a Flask-based web application that allows users to create, organize, and manage their personal video game libraries.  
The project was built as the final project for [CS50x](https://cs50.harvard.edu/x/) and is designed to demonstrate practical web development skills with Python, Flask, SQLAlchemy, and front-end integration.  

With **Gamer's History**, players can:  
- Import games from external platforms (currently Steam, with plans for Epic Games and GOG).  
- Manually add games with custom details.  
- Upload and display **cover images** for each game.  
- Track **hours played**, add personal notes, and rate their games.  
- Switch between **list view** (table-based) and **grid/tile view** (visual cards).  
- Enjoy multilingual support with English and Ukrainian translations.  

The goal of the project is to provide gamers with a simple but powerful way to keep track of their collections, reflect on their gaming history, and share it with others.  

---

## Features  

### User Authentication  
- Secure login and registration system based on **username** (not email).  
- Passwords are securely hashed before storage.  
- Session management handled via **Flask-Login**.  

### Game Management  
- Add, edit, and delete games from your personal library.  
- Edit includes updating title, platform, year, hours played, and rating.  
- Duplicate prevention: the same game cannot be added twice.  

### Cover Uploads  
- Users can upload local images or fetch covers from external APIs.  
- File validation ensures only safe extensions (`png`, `jpg`, `jpeg`, `gif`).  
- Covers are stored in the `static/uploads` folder.  

### Views  
- **List view:** shows games in a table with hours, ratings, and edit/delete actions.  
- **Tile view:** shows games as cards with cover images and quick stats.  
- Users can switch views via toggle buttons.  

### Ratings & Playtime  
- Each game in the library can be rated on a scale of 1–10.  
- Hours played are stored as numeric values and displayed in both views.  

### Internationalization  
- **Flask-Babel** handles translations.  
- Language can be switched via `?lang=uk` or `?lang=en`.  
- Translations stored in `translations/en/` and `translations/uk/`.  

---

## Technologies  
- **Backend:** [Flask](https://flask.palletsprojects.com/) (Python)  
- **Database:** SQLite with SQLAlchemy ORM  
- **Frontend:** HTML, CSS, Bootstrap 5, Jinja2 templates  
- **Other:** Flask-Migrate (migrations), Flask-Login (authentication), Flask-Babel (i18n)  

---

## Installation & Setup  

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

## Usage Example

1. Register an account or log in with your username.

2. Add a game manually (enter title, platform, year, hours, rating).

3. Upload a cover image (optional).

4. Switch between list and tile view to browse your library.

5. Edit or delete games whenever needed.

6. Change the language to Ukrainian by appending ?lang=uk to the URL.

---

## Project Structure
gamers-history/
│── app.py              # Main Flask application
│── models.py           # Database models (User, Game, UserGame)
│── forms.py            # Flask-WTF forms
│── templates/          # Jinja2 templates
│   ├── base.html
│   ├── games/
│   │   ├── list.html
│   │   └── tiles.html
│── static/             # CSS, JS, uploaded covers
│── translations/       # i18n files (en, uk)
│── migrations/         # Database migrations
│── requirements.txt
│── README.md

---

## Design Decisions

Flask over Django: lightweight, minimal boilerplate, perfect for CS50 project scope.

SQLite: simple, file-based DB ideal for personal apps. Can be replaced with PostgreSQL/MySQL in production.

Username-based login: avoids complexity of email verification.

Two view modes: inspired by Steam/Epic UI, giving users choice of data-focused or visual browsing.

CSRF protection: all forms include CSRF tokens via Flask-WTF.

---

## Internationalization

All templates use _('text') for translatable strings.

babel.cfg specifies extraction rules.

Workflow:

pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d translations
pybabel compile -d translations


Add new language by creating a new folder under translations/ and repeating the update/compile steps.

---

## AI Assistance
Some parts of this project were developed with the help of AI tools:
- ChatGPT (OpenAI) for code snippets (form handling, pagination, etc).
- GitHub Copilot for auto-completion in Flask routes.

---

## License

This project is licensed under the MIT License.
You are free to use, modify, and distribute it, provided proper credit is given.

---

## Credits

Built as part of CS50x Final Project.

RAWG API for game metadata and images.

Flask community for extensions: Flask-Login, Flask-Migrate, Flask-Babel.