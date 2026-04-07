import os
import re
import random
import threading
import smtplib
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_mail import Mail, Message
from bson.objectid import ObjectId
from db import users_collection, assignments_collection, submissions_collection, classes_collection, student_classes_collection
from utils.text_extractor import extract_text
from utils.similarity import calculate_similarity, get_status, get_status_color
from utils.ai_detector import detect_ai_content

# ─── Load .env ─────────────────────────────────────────────────────
load_dotenv()

# ─── Flask App Setup ───────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "plagiarism_checker_dev_key")

# Upload folder config
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {"pdf", "docx"}

# ─── Flask-Mail Config (Gmail SMTP) ───────────────────────────────
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_TIMEOUT"] = 10
mail = Mail(app)


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


def generate_otp():
    """Generate a random 6-digit OTP."""
    return str(random.randint(100000, 999999))


def is_valid_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def send_otp_email(to_email, otp, subject_prefix="Verification"):
    """Send OTP via Flask-Mail (Gmail SMTP) synchronously with debug logging."""
    # Always print OTP to console as a development/demo fallback
    print(f"\n" + "="*50)
    print(f"[DEBUG] Attempting to send {subject_prefix} OTP to: {to_email}")
    print(f"[DEBUG] OTP Code: {otp}")
    print(f"="*50 + "\n")

    try:
        html_body = f"""
        <html>
        <body style="font-family: 'Inter', sans-serif; background: #0a0e1a; color: #f1f5f9; padding: 40px; margin: 0;">
            <div style="max-width: 500px; margin: 0 auto; background: #111827; border-radius: 20px; padding: 40px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <div style="display: inline-block; width: 60px; height: 60px; background: rgba(59,130,246,0.1); border-radius: 50%; line-height: 60px; font-size: 30px; color: #3b82f6;">&#128737;</div>
                </div>
                <h2 style="text-align: center; color: #f1f5f9; margin-bottom: 10px; font-weight: 700;">{subject_prefix} Code</h2>
                <p style="text-align: center; color: #94a3b8; margin-bottom: 30px; font-size: 16px;">Use the code below to securely verify your identity.</p>
                
                <div style="text-align: center; background: rgba(59,130,246,0.05); border: 1px dashed rgba(59,130,246,0.3); border-radius: 12px; padding: 25px; margin-bottom: 30px;">
                    <h1 style="margin: 0; font-size: 42px; letter-spacing: 10px; color: #3b82f6; font-family: monospace;">{otp}</h1>
                </div>
                
                <p style="text-align: center; color: #64748b; font-size: 14px; line-height: 1.6;">
                    This code will expire in <strong>10 minutes</strong>.<br>
                    If you didn't request this code, you can safely ignore this email.
                </p>
                <div style="margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 20px; text-align: center;">
                    <p style="color: #475569; font-size: 12px;">&copy; 2026 AI Plagiarism Checker. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg = Message(
            subject=f"AI Plagiarism Checker — {subject_prefix} OTP",
            recipients=[to_email],
            html=html_body,
        )
        
        # ─── Render Pre-flight SMTP Check ───
        print(f"[RENDER-LOG] Testing SMTP connection before sending to {to_email}...")
        try:
            smtp_server = smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"], timeout=10)
            smtp_server.starttls()
            smtp_server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            print("[RENDER-LOG] SMTP login success! Proceeding to send...")
            smtp_server.quit()
        except Exception as smtp_err:
            print(f"[RENDER-LOG] SMTP Connection Test Failed: {smtp_err}")
            # We don't return False here, we try with Flask-Mail anyway but we have the log.

        print("[RENDER-LOG] Before mail send attempt...")
        
        # Send synchronously within app context for clarity
        with app.app_context():
            mail.send(msg)
            
        print(f"[RENDER-LOG] After mail send attempt. Success! (Check: {to_email})")
        return True
        
    except Exception as e:
        print(f"\n[RENDER-LOG] !!! MAIL ERROR !!!")
        print(f"[RENDER-LOG] Exception Details: {str(e)}")
        print(f"[RENDER-LOG] If this is a timeout, check Render Outbound IP settings or use an API-based mail service (SendGrid).\n")
        return False


# ─── Homepage ──────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/test-mail")
def test_mail():
    """Route to manually test OTP email sending."""
    test_email = os.environ.get("MAIL_USERNAME")
    test_otp = "123456"
    print(f"[DEBUG] Triggering test mail to {test_email}...")
    
    if send_otp_email(test_email, test_otp, subject_prefix="TEST"):
        return f"<h1>Test email attempt finished!</h1><p>Check console for debug logs. If successful, check inbox for: {test_email}</p>"
    else:
        return "<h1>Test email failed!</h1><p>Check console for the detailed error message.</p>"




# ─── Help Page ─────────────────────────────────────────────────────
@app.route("/help")
def help_page():
    return render_template("help.html")


# ─── Register ─────────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        # Validate email format
        if not is_valid_email(email):
            flash("Invalid email address. Please enter a valid email.", "danger")
            return render_template("register.html", role=role)

        # Check if user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("Email already registered. Please login.", "danger")
            return redirect(url_for("login", role=role))

        # Generate OTP
        otp = generate_otp()
        
        # Store pending registration in session
        session["pending_registration"] = {
            "name": name,
            "email": email,
            "password": password,
            "role": role,
            "otp": otp,
            "timestamp": datetime.now().isoformat(),
        }
        session.modified = True

        # Send OTP email
        if send_otp_email(email, otp, subject_prefix="Registration"):
            flash("Verification code sent to your email!", "success")
        else:
            flash("Email system is busy, but we've generated your code. Check console for development.", "warning")

        return redirect(url_for("verify_otp_page"))

    role = request.args.get("role", "student")
    return render_template("register.html", role=role)


@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp_page():
    pending = session.get("pending_registration")
    if not pending:
        flash("Registration session expired. Please register again.", "danger")
        return redirect(url_for("register"))

    if request.method == "POST":
        # Check expiry (10 minutes)
        timestamp = datetime.fromisoformat(pending["timestamp"])
        if (datetime.now() - timestamp).total_seconds() > 600:
            session.pop("pending_registration", None)
            flash("OTP expired. Please register again.", "danger")
            return redirect(url_for("register"))

        # Collect OTP from 6 individual inputs (d1..d6)
        entered_otp = "".join([request.form.get(f"d{i}", "") for i in range(1, 7)])
        stored_otp = pending.get("otp", "")

        if entered_otp == stored_otp:
            # OTP correct — create user
            user = {
                "name": pending["name"],
                "email": pending["email"],
                "password": pending["password"],
                "role": pending["role"],
                "created_at": datetime.now()
            }
            users_collection.insert_one(user)
            session.pop("pending_registration", None)
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login", role=pending["role"]))
        else:
            flash("Invalid OTP. Please try again.", "danger")

    return render_template("verify_otp.html", email=pending["email"], role=pending["role"])


@app.route("/resend-otp")
def resend_otp():
    # Handle both registration and password reset resends
    if "pending_registration" in session:
        data = session["pending_registration"]
        new_otp = generate_otp()
        data["otp"] = new_otp
        data["timestamp"] = datetime.now().isoformat()
        session.modified = True
        send_otp_email(data["email"], new_otp, subject_prefix="Registration")
        flash("A new registration code has been sent!", "success")
        return redirect(url_for("verify_otp_page"))
        
    elif "reset_password" in session:
        data = session["reset_password"]
        new_otp = generate_otp()
        data["otp"] = new_otp
        data["timestamp"] = datetime.now().isoformat()
        session.modified = True
        send_otp_email(data["email"], new_otp, subject_prefix="Password Reset")
        flash("A new reset code has been sent!", "success")
        return redirect(url_for("verify_reset_otp"))
        
    flash("No active request found to resend code.", "danger")
    return redirect(url_for("index"))


# ─── Forgot Password ───────────────────────────────────────────────
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        role = request.form.get("role", "student")

        user = users_collection.find_one({"email": email})
        if not user:
            flash("Email not found. Please check and try again.", "danger")
            return redirect(url_for("forgot_password", role=role))

        # Generate and send OTP
        otp = generate_otp()
        session["reset_password"] = {
            "email": email,
            "otp": otp,
            "timestamp": datetime.now().isoformat(),
            "verified": False
        }
        session.modified = True

        if send_otp_email(email, otp, subject_prefix="Password Reset"):
            flash("A password reset code has been sent to your email.", "success")
        else:
            flash("Email system busy. Please check console or try again.", "warning")

        return redirect(url_for("verify_reset_otp"))

    role = request.args.get("role", "student")
    return render_template("forgot_password.html", role=role)


# ─── Verify Reset OTP ──────────────────────────────────────────────
@app.route("/verify-reset-otp", methods=["GET", "POST"])
def verify_reset_otp():
    reset_data = session.get("reset_password")
    if not reset_data:
        flash("Password reset session expired. Please try again.", "danger")
        return redirect(url_for("forgot_password"))
        
    email = reset_data["email"]

    if request.method == "POST":
        # Check expiry (5 minutes)
        timestamp = datetime.fromisoformat(reset_data["timestamp"])
        if (datetime.now() - timestamp).total_seconds() > 300:
            session.pop("reset_password", None)
            flash("OTP expired. Please request a new one.", "danger")
            return redirect(url_for("forgot_password"))

        entered_otp = "".join([request.form.get(f"d{i}", "") for i in range(1, 7)])
        stored_otp = reset_data.get("otp", "")

        if entered_otp == stored_otp:
            session["reset_password"]["verified"] = True
            flash("OTP verified! You can now reset your password.", "success")
            return redirect(url_for("reset_password"))
        else:
            flash("Invalid OTP. Please try again.", "danger")

    return render_template("verify_reset_otp.html", email=email)


# ─── Reset Password ────────────────────────────────────────────────
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    reset_data = session.get("reset_password")
    if not reset_data or not reset_data.get("verified"):
        flash("Unauthorized access. Please verify your OTP first.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("reset_password"))
            
        if len(new_password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for("reset_password"))

        # Update in DB
        email = reset_data["email"]
        users_collection.update_one(
            {"email": email},
            {"$set": {"password": new_password}}
        )

        session.pop("reset_password", None)
        flash("Password has been reset successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html")


# ─── Login ─────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

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

    student_id = session["user_id"]
    
    # Get all joined class IDs
    joined_classes = list(student_classes_collection.find({"student_id": student_id}))
    class_ids = [c["class_id"] for c in joined_classes]
    
    # Fetch classes info
    classes = list(classes_collection.find({"class_id": {"$in": class_ids}}))
    
    # Fetch assignments for joined classes
    assignments = list(assignments_collection.find({"class_id": {"$in": class_ids}}))
    
    return render_template("student_dashboard.html", classes=classes, assignments=assignments)


# ─── Join Class (Student) ─────────────────────────────────────────
@app.route("/student/join_class", methods=["GET", "POST"])
def join_class():
    if not login_required(role="student"):
        flash("Please login as a student.", "warning")
        return redirect(url_for("login", role="student"))

    if request.method == "POST":
        join_code = request.form.get("join_code")
        student_id = session["user_id"]

        # Find class by join code
        cls = classes_collection.find_one({"join_code": join_code})
        if not cls:
            flash("Invalid join code. Please check and try again.", "danger")
            return redirect(url_for("join_class"))

        # Check if already joined
        existing = student_classes_collection.find_one({
            "student_id": student_id,
            "class_id": cls["class_id"]
        })
        if existing:
            flash("You have already joined this class.", "info")
            return redirect(url_for("student_dashboard"))

        # Map student to class
        student_classes_collection.insert_one({
            "student_id": student_id,
            "class_id": cls["class_id"]
        })
        
        flash(f"Successfully joined {cls['class_name']}!", "success")
        return redirect(url_for("student_dashboard"))

    return render_template("join_class.html")


# ─── Upload Assignment (Student) ──────────────────────────────────
@app.route("/upload/<assignment_id>", methods=["GET", "POST"])
def upload(assignment_id):
    if not login_required(role="student"):
        flash("Please login as a student.", "warning")
        return redirect(url_for("login", role="student"))

    # Fetch assignment details
    assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
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

        # Rename file: studentID_assignmentID_filename
        student_id = session["user_id"]
        original_filename = file.filename
        new_filename = f"{student_id}_{assignment_id}_{original_filename}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)
        file.save(file_path)

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

        # ── Detect AI-generated content (Dual-layer check) ──
        ai_score = detect_ai_content(extracted_text)

        # Save submission to MongoDB
        submission = {
            "student_id": student_id,
            "student_name": session.get("user_name", "Unknown"),
            "assignment_id": assignment_id,
            "file_path": file_path,
            "filename": original_filename,
            "extracted_text": extracted_text,
            "ai_score": ai_score,
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

    faculty_id = session["user_id"]
    
    # Fetch classes created by this faculty
    classes = list(classes_collection.find({"faculty_id": faculty_id}))
    
    # Fetch assignments created by this faculty
    assignments = list(assignments_collection.find({"created_by": faculty_id}))
    
    return render_template("faculty_dashboard.html", classes=classes, assignments=assignments)


# ─── Create Class (Faculty) ───────────────────────────────────────
@app.route("/faculty/create_class", methods=["GET", "POST"])
def create_class():
    if not login_required(role="faculty"):
        flash("Please login as faculty.", "warning")
        return redirect(url_for("login", role="faculty"))

    if request.method == "POST":
        class_name = request.form.get("class_name")
        faculty_id = session["user_id"]
        
        # Generate unique join code
        while True:
            join_code = str(random.randint(100000, 999999))
            if not classes_collection.find_one({"join_code": join_code}):
                break
        
        class_id = str(ObjectId())
        
        new_class = {
            "class_id": class_id,
            "class_name": class_name,
            "faculty_id": faculty_id,
            "join_code": join_code,
            "created_at": datetime.now()
        }
        classes_collection.insert_one(new_class)
        
        flash(f"Class '{class_name}' created successfully! Code: {join_code}", "success")
        return redirect(url_for("faculty_dashboard"))

    return render_template("create_class.html")


# ─── Create Assignment (Faculty) ──────────────────────────────────
@app.route("/create_assignment", methods=["GET", "POST"])
def create_assignment():
    if not login_required(role="faculty"):
        flash("Please login as faculty.", "warning")
        return redirect(url_for("login", role="faculty"))

    faculty_id = session["user_id"]
    # Fetch classes for the dropdown
    classes = list(classes_collection.find({"faculty_id": faculty_id}))

    if request.method == "POST":
        subject = request.form.get("subject")
        title = request.form.get("title")
        class_id = request.form.get("class_id")

        if not class_id:
            flash("Please select a class for the assignment.", "danger")
            return redirect(url_for("create_assignment"))

        assignment = {
            "subject": subject,
            "title": title,
            "class_id": class_id,
            "created_by": faculty_id,
            "created_at": datetime.now(),
        }
        assignments_collection.insert_one(assignment)
        flash("Assignment created successfully!", "success")
        return redirect(url_for("faculty_dashboard"))

    return render_template("create_assignment.html", classes=classes)


# ─── View Submissions (Faculty) ───────────────────────────────────
@app.route("/faculty/submissions/<assignment_id>")
def view_submissions(assignment_id):
    if not login_required(role="faculty"):
        flash("Please login as faculty.", "warning")
        return redirect(url_for("login", role="faculty"))

    # Fetch assignment details
    assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
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
            similar_user = users_collection.find_one(
                {"_id": ObjectId(sub["most_similar_student"])}
            )
            sub["similar_student_name"] = similar_user["name"] if similar_user else "Unknown"
        else:
            sub["similar_student_name"] = "N/A"

    return render_template(
        "submissions.html",
        assignment=assignment,
        submissions=submissions,
    )


# ─── View File (Faculty) ──────────────────────────────────────────
@app.route("/faculty/view_file/<submission_id>")
def view_file(submission_id):
    if not login_required(role="faculty"):
        flash("Please login as faculty.", "warning")
        return redirect(url_for("login", role="faculty"))

    submission = submissions_collection.find_one({"_id": ObjectId(submission_id)})
    if not submission:
        flash("Submission not found.", "danger")
        return redirect(url_for("faculty_dashboard"))

    file_path = submission.get("file_path")
    if not file_path or not os.path.exists(file_path):
        flash("File not found on server.", "danger")
        return redirect(url_for("faculty_dashboard"))

    # Security check: Ensure faculty is viewing an assignment they created or has access to
    # (For now, we just check role, but could be more restrictive if needed)

    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)

    return send_from_directory(directory, filename)


# ─── Run the App ──────────────────────────────────────────────────
if __name__ == "__main__":
    # Ensure upload folder exists
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
        
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
