from contextlib import closing
from functools import wraps
import logging
import os
from pathlib import Path
import re
import secrets
import sqlite3
from uuid import uuid4

from flask import Flask, abort, flash, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


ROOT_DIR = Path(__file__).resolve().parent
STORAGE_DIR = Path(os.environ.get("MATH_IDENTITY_STORAGE_DIR", ROOT_DIR))
DATABASE_PATH = Path(os.environ.get("MATH_IDENTITY_DATABASE", STORAGE_DIR / "database" / "users.db"))
CATEGORIES = ("company", "college", "school", "vehicle", "phone")
DATA_DIRS = {category: STORAGE_DIR / "data" / category for category in CATEGORIES}
GENERATED_DIRS = {category: STORAGE_DIR / "generated" / category for category in CATEGORIES}
STYLE_OPTIONS = (
	"Classic Standard (Arial)",
	"Artistic Stylized (Gabriola)",
	"Cursive Script (Vladimir)",
	"Playful Stylized (Comic Bold)",
)
COMPANY_STYLE_OPTIONS = ("Cursive Script (Vladimir)", "Serif", "Sans Serif", "Monospace")
BOARD_OPTIONS = ("12th Board (HSC)", "10th Board (SSLC)")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
logging.basicConfig(level=logging.INFO)


def initialize_directories():
	for directory in (DATABASE_PATH.parent, *DATA_DIRS.values(), *GENERATED_DIRS.values()):
		directory.mkdir(parents=True, exist_ok=True)


def initialize_database():
	initialize_directories()
	with closing(sqlite3.connect(DATABASE_PATH)) as connection:
		connection.execute(
			"CREATE TABLE IF NOT EXISTS users ("
			"user_id TEXT PRIMARY KEY, password_hash TEXT NOT NULL)"
		)
		connection.commit()


def login_required(view):
	@wraps(view)
	def wrapped_view(*args, **kwargs):
		if "user_id" not in session:
			return redirect(url_for("login"))
		return view(*args, **kwargs)
	return wrapped_view


def _category_context(category, output_path=None):
	labels = {
		"company": ("Ticker symbol", "Display corporate name", "Company"),
		"college": ("College ID", "College name", "College"),
		"school": ("School ID", "School name", "School"),
		"vehicle": ("Vehicle ID", "Brand name", "Vehicle"),
		"phone": ("Model ID", "Brand name", "Phone"),
	}
	identifier_label, name_label, title = labels[category]
	return {
		"category": category,
		"title": title,
		"identifier_label": identifier_label,
		"name_label": name_label,
		"identifier_field": "ticker" if category == "company" else "college_id" if category == "college" else "school_id" if category == "school" else "vehicle_id" if category == "vehicle" else "model_id",
		"name_field": "company_name" if category == "company" else "college_name" if category == "college" else "school_name" if category == "school" else "brand_name",
		"styles": COMPANY_STYLE_OPTIONS if category == "company" else STYLE_OPTIONS,
		"boards": BOARD_OPTIONS,
		"image_url": url_for("generated_file", category=category, filename=output_path.name) if output_path else None,
	}


def _render_category(category, output_path=None, status=200):
	return render_template(f"{category}.html", **_category_context(category, output_path)), status


def _run_generator(category, identifier, display_name, style, board):
	output_dir = GENERATED_DIRS[category]
	if category == "company":
		from modules.company import generate_company
		return generate_company(identifier, display_name, style, output_dir, show_dialog=False)
	if category == "college":
		from modules.college import generate_college
		return generate_college(identifier, display_name, style, output_dir)
	if category == "school":
		from modules.school import generate_school
		return generate_school(identifier, display_name, board, style, output_dir)
	if category == "vehicle":
		from modules.vehicle import generate_vehicle
		return generate_vehicle(identifier, display_name, style, output_dir)
	from modules.phone import generate_phone
	return generate_phone(identifier, display_name, style, output_dir)


@app.get("/")
def index():
	return redirect(url_for("dashboard" if "user_id" in session else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		user_id = request.form.get("user_id", "").strip()
		password = request.form.get("password", "")
		with closing(sqlite3.connect(DATABASE_PATH)) as connection:
			user = connection.execute(
				"SELECT password_hash FROM users WHERE user_id = ?", (user_id,)
			).fetchone()
		if user and check_password_hash(user[0], password):
			session.clear()
			session["user_id"] = user_id
			return redirect(url_for("dashboard"))
		flash("The user ID or password is incorrect.", "error")
	return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		user_id = request.form.get("user_id", "").strip()
		password = request.form.get("password", "")
		confirmation = request.form.get("confirm_password", "")
		if not re.fullmatch(r"[A-Za-z0-9_-]{3,32}", user_id):
			flash("User ID must be 3-32 letters, numbers, underscores, or hyphens.", "error")
		elif len(password) < 8:
			flash("Password must contain at least eight characters.", "error")
		elif password != confirmation:
			flash("The passwords do not match.", "error")
		else:
			try:
				with closing(sqlite3.connect(DATABASE_PATH)) as connection:
					connection.execute(
						"INSERT INTO users (user_id, password_hash) VALUES (?, ?)",
						(user_id, generate_password_hash(password)),
					)
					connection.commit()
			except sqlite3.IntegrityError:
				flash("That user ID is already registered.", "error")
			else:
				flash("Account created. Sign in to continue.", "success")
				return redirect(url_for("login"))
	return render_template("register.html")


@app.get("/dashboard")
@login_required
def dashboard():
	return render_template("dashboard.html")


@app.get("/company", endpoint="company")
@login_required
def company_page():
	return _render_category("company")


@app.get("/college", endpoint="college")
@login_required
def college_page():
	return _render_category("college")


@app.get("/school", endpoint="school")
@login_required
def school_page():
	return _render_category("school")


@app.get("/vehicle", endpoint="vehicle")
@login_required
def vehicle_page():
	return _render_category("vehicle")


@app.get("/phone", endpoint="phone")
@login_required
def phone_page():
	return _render_category("phone")


@app.post("/generate/<category>")
@login_required
def generate_category(category):
	if category not in CATEGORIES:
		abort(404)
	identifier = request.form.get(_category_context(category)["identifier_field"], "").strip()
	display_name = request.form.get(_category_context(category)["name_field"], "").strip()
	style = request.form.get("style", request.form.get("text_style", STYLE_OPTIONS[0]))
	board = request.form.get("board_type", BOARD_OPTIONS[0])
	if not identifier or not display_name:
		flash("Enter both identity fields before generating.", "error")
		return _render_category(category, status=400)
	allowed_styles = COMPANY_STYLE_OPTIONS if category == "company" else STYLE_OPTIONS
	if style not in allowed_styles or (category == "school" and board not in BOARD_OPTIONS):
		flash("Choose one of the available style and category options.", "error")
		return _render_category(category, status=400)
	if category == "company":
		valid_identity = re.fullmatch(r"[A-Za-z0-9.^_-]{1,12}", identifier) and len(display_name) <= 80
	else:
		valid_identity = len(identifier) <= 40 and len(display_name) <= 80
	if not valid_identity:
		flash("The identity fields contain unsupported characters or are too long.", "error")
		return _render_category(category, status=400)
	try:
		output_path = _run_generator(category, identifier.upper(), display_name, style, board)
		if not output_path.is_file():
			raise OSError("The generator did not create an output image.")
	except ValueError as error:
		app.logger.info("Rejected %s generation input: %s", category, error)
		flash(str(error), "error")
		return _render_category(category, status=400)
	except Exception:
		app.logger.exception("Could not generate %s identity", category)
		flash("Unable to generate the visualization. Please check the entered details.", "error")
		return _render_category(category, status=500)
	return _render_category(category, output_path)


@app.get("/generated/<category>/<path:filename>")
@login_required
def generated_file(category, filename):
	if category not in CATEGORIES:
		abort(404)
	return send_from_directory(GENERATED_DIRS[category], filename)


@app.get("/logout")
def logout():
	session.clear()
	return redirect(url_for("login"))


initialize_database()

if __name__ == "__main__":
	app.run(
		host="0.0.0.0",
		port=int(os.environ.get("PORT", "5000")),
		debug=os.environ.get("FLASK_DEBUG") == "1",
	)
 