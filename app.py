import os
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from db import users_collection, assignments_collection, submissions_collection
from utils.text_extractor import extract_text
from utils.similarity import calculate_similarity, get_status, get_status_color

# Load environment variables
load_dotenv()

# ─── Flask App Setup ───────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-default-key")

# Upload folder config
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "docx"}

# ─── Logging Setup ─────────────────────────────────────────────────
logging.basicConfig(
    filename="app.log",
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ─── Rate Limiting ─────────────────────────────────────────────────
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )
except ImportError:
    # flask-limiter not installed — create a dummy decorator so routes still work
    limiter = None
    logger.warning("flask-limiter not installed. Rate limiting is DISABLED.")


def rate_limit(limit_string):
    """Apply rate limit if flask-limiter is available, otherwise no-op."""
    if limiter:
        return limiter.limit(limit_string)
    # Return a no-op decorator
    def decorator(f):
        return f
    return decorator


# ─── Input Validation Helpers ──────────────────────────────────────
def is_valid_email(email):
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def sanitize_text(text):
    """Remove potentially dangerous characters from user input."""
    if not text:
        return ""
    # Strip leading/trailing whitespace and limit length
    text = text.strip()[:200]
    # Remove any HTML/script tags
    text = re.sub(r"<[^>]*>", "", text)
    return text


def is_valid_role(role):
    """Ensure role is only student or faculty."""
    return role in ("student", "faculty")


def allowed_file(filename):
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── Helper: Login Required ────────────────────────────────────────
def login_required(role=None):
    """Check if user is logged in and has the correct role."""
    if "user_id" not in session:
        return False
    if role and session.get("user_role") != role:
        return False
    return True


# ─── Error Handlers ────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    flash("Page not found.", "warning")
    return redirect(url_for("index"))


@app.errorhandler(413)
def file_too_large(e):
    flash("File is too large. Maximum size is 10 MB.", "danger")
    return redirect(request.referrer or url_for("index"))


@app.errorhandler(429)
def rate_limit_exceeded(e):
    logger.warning(f"Rate limit exceeded from IP: {request.remote_addr}")
    flash("Too many requests. Please wait and try again.", "danger")
    return redirect(request.referrer or url_for("index"))


@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    flash("Something went wrong. Please try again later.", "danger")
    return redirect(url_for("index"))


# ─── Homepage ──────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ─── Register ─────────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
@rate_limit("10 per minute")
def register():
    if request.method == "POST":
        name = sanitize_text(request.form.get("name"))
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "")

        # ── Input Validation ──
        if not name or len(name) < 2:
            flash("Name must be at least 2 characters.", "danger")
            return redirect(request.url)

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "danger")
            return redirect(request.url)

        if len(password) < 4:
            flash("Password must be at least 4 characters.", "danger")
            return redirect(request.url)

        if not is_valid_role(role):
            flash("Invalid role selected.", "danger")
            return redirect(request.url)

        # Check if user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("Email already registered. Please login.", "danger")
            return redirect(url_for("login", role=role))

        # Create new user
        user = {
            "name": name,
            "email": email,
            "password": password,  # Plain text (as per requirements)
            "role": role,
        }
        users_collection.insert_one(user)
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login", role=role))

    role = request.args.get("role", "student")
    return render_template("register.html", role=role)


# ─── Login ─────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
@rate_limit("5 per minute")
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "")

        # ── Input Validation ──
        if not is_valid_email(email) or not password or not is_valid_role(role):
            flash("Invalid email, password, or role.", "danger")
            logger.warning(f"Invalid login attempt from IP: {request.remote_addr}")
            return redirect(url_for("login", role=role))

        # Find user in MongoDB
        user = users_collection.find_one({
            "email": email,
            "password": password,
            "role": role,
        })

        if user:
            session["user_id"] = str(user["_id"])
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            flash(f"Welcome, {user['name']}!", "success")

            if role == "student":
                return redirect(url_for("student_dashboard"))
            else:
                return redirect(url_for("faculty_dashboard"))
        else:
            logger.warning(f"Failed login for email: {email} from IP: {request.remote_addr}")
            flash("Invalid email, password, or role.", "danger")
            return redirect(url_for("login", role=role))

    role = request.args.get("role", "student")
    return render_template("login.html", role=role)


# ─── Logout ────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))


# ─── Student Dashboard ────────────────────────────────────────────
@app.route("/student/dashboard")
def student_dashboard():
    if not login_required(role="student"):
        flash("Please login as a student.", "warning")
        return redirect(url_for("login", role="student"))

    # Fetch all assignments from MongoDB
    assignments = list(assignments_collection.find())
    return render_template("student_dashboard.html", assignments=assignments)


# ─── Upload Assignment (Student) ──────────────────────────────────
@app.route("/upload/<assignment_id>", methods=["GET", "POST"])
@rate_limit("10 per minute")
def upload(assignment_id):
    if not login_required(role="student"):
        flash("Please login as a student.", "warning")
        return redirect(url_for("login", role="student"))

    # Validate assignment_id format
    try:
        obj_id = ObjectId(assignment_id)
    except Exception:
        flash("Invalid assignment.", "danger")
        return redirect(url_for("student_dashboard"))

    # Fetch assignment details
    assignment = assignments_collection.find_one({"_id": obj_id})
    if not assignment:
        flash("Assignment not found.", "danger")
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            flash("No file selected.", "danger")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Invalid file type. Only PDF and DOCX files are allowed.", "danger")
            return redirect(request.url)

        # Sanitize and rename file: studentID_assignmentID_filename
        student_id = session["user_id"]
        original_filename = secure_filename(file.filename)  # Sanitize filename
        new_filename = f"{student_id}_{assignment_id}_{original_filename}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)

        try:
            file.save(file_path)
        except Exception as e:
            logger.error(f"File save failed: {e}")
            flash("File upload failed. Please try again.", "danger")
            return redirect(request.url)

        # Extract text from file
        extracted_text = extract_text(file_path)

        # ── Compare with previous submissions for same assignment ──
        previous_submissions = list(submissions_collection.find({
            "assignment_id": assignment_id,
            "student_id": {"$ne": student_id},
        }))

        similarity_results = []
        highest_score = 0.0
        most_similar_student = None

        for prev in previous_submissions:
            prev_text = prev.get("extracted_text", "")
            if prev_text:
                score = calculate_similarity(extracted_text, prev_text)
                similarity_results.append({
                    "matched_with": prev["student_id"],
                    "score": score,
                })
                if score > highest_score:
                    highest_score = score
                    most_similar_student = prev["student_id"]

        # Save submission to MongoDB
        submission = {
            "student_id": student_id,
            "student_name": session.get("user_name", "Unknown"),
            "assignment_id": assignment_id,
            "file_path": file_path,
            "filename": original_filename,
            "extracted_text": extracted_text,
            "similarity_results": similarity_results,
            "highest_similarity_score": highest_score,
            "most_similar_student": most_similar_student,
            "timestamp": datetime.now(),
        }
        submissions_collection.insert_one(submission)

        flash("Assignment submitted successfully!", "success")
        return redirect(url_for("student_dashboard"))

    return render_template("upload.html", assignment=assignment)


# ─── Faculty Dashboard ────────────────────────────────────────────
@app.route("/faculty/dashboard")
def faculty_dashboard():
    if not login_required(role="faculty"):
        flash("Please login as faculty.", "warning")
        return redirect(url_for("login", role="faculty"))

    # Fetch assignments created by this faculty
    faculty_id = session["user_id"]
    assignments = list(assignments_collection.find({"created_by": faculty_id}))
    return render_template("faculty_dashboard.html", assignments=assignments)


# ─── Create Assignment (Faculty) ──────────────────────────────────
@app.route("/create_assignment", methods=["GET", "POST"])
@rate_limit("10 per minute")
def create_assignment():
    if not login_required(role="faculty"):
        flash("Please login as faculty.", "warning")
        return redirect(url_for("login", role="faculty"))

    if request.method == "POST":
        subject = sanitize_text(request.form.get("subject"))
        title = sanitize_text(request.form.get("title"))
        faculty_id = session["user_id"]

        # ── Input Validation ──
        if not subject or len(subject) < 2:
            flash("Subject name must be at least 2 characters.", "danger")
            return redirect(request.url)

        if not title or len(title) < 2:
            flash("Assignment title must be at least 2 characters.", "danger")
            return redirect(request.url)

        assignment = {
            "subject": subject,
            "title": title,
            "created_by": faculty_id,
            "created_at": datetime.now(),
        }
        assignments_collection.insert_one(assignment)
        flash("Assignment created successfully!", "success")
        return redirect(url_for("faculty_dashboard"))

    return render_template("create_assignment.html")


# ─── View Submissions (Faculty) ───────────────────────────────────
@app.route("/faculty/submissions/<assignment_id>")
def view_submissions(assignment_id):
    if not login_required(role="faculty"):
        flash("Please login as faculty.", "warning")
        return redirect(url_for("login", role="faculty"))

    # Validate assignment_id format
    try:
        obj_id = ObjectId(assignment_id)
    except Exception:
        flash("Invalid assignment.", "danger")
        return redirect(url_for("faculty_dashboard"))

    # Fetch assignment details
    assignment = assignments_collection.find_one({"_id": obj_id})
    if not assignment:
        flash("Assignment not found.", "danger")
        return redirect(url_for("faculty_dashboard"))

    # Fetch all submissions sorted by highest similarity
    submissions = list(submissions_collection.find(
        {"assignment_id": str(assignment_id)}
    ).sort("highest_similarity_score", -1))

    # Add status and color info to each submission
    for sub in submissions:
        score = sub.get("highest_similarity_score", 0)
        sub["status"] = get_status(score)
        sub["status_color"] = get_status_color(score)

        # Get the name of the most similar student
        if sub.get("most_similar_student"):
            try:
                similar_user = users_collection.find_one(
                    {"_id": ObjectId(sub["most_similar_student"])}
                )
                sub["similar_student_name"] = similar_user["name"] if similar_user else "Unknown"
            except Exception:
                sub["similar_student_name"] = "Unknown"
        else:
            sub["similar_student_name"] = "N/A"

    return render_template(
        "submissions.html",
        assignment=assignment,
        submissions=submissions,
    )


# ─── Run the App ──────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
