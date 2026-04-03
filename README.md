# 🛡️ AI Assignment Plagiarism Checker

A web-based plagiarism detection system built with **Flask** and **MongoDB**. Faculty can create assignments, students can upload submissions (PDF/DOCX), and the system automatically detects plagiarism using **TF-IDF similarity analysis**.

---

## 📋 Features

- **Role-Based Authentication** — Separate login for Students and Faculty
- **Student Dashboard** — View assignments and upload submissions
- **Faculty Dashboard** — Create assignments and manage submissions
- **File Upload** — Accepts PDF and DOCX files with validation (max 10 MB)
- **Text Extraction** — Automatically extracts text from uploaded documents
- **Plagiarism Detection** — TF-IDF + Cosine Similarity comparison engine
- **Color-Coded Reports** — Green (Safe), Yellow (Suspicious), Red (High Plagiarism)
- **MongoDB Atlas** — Cloud-based persistent data storage

---

## 🔒 Security Features

| Feature | Description |
|---------|-------------|
| **Environment Variables** | All secrets stored in `.env` (never committed) |
| **Rate Limiting** | Login: 5/min, Upload: 10/min, General: 50/hr |
| **Input Validation** | Email format, password length, text sanitization |
| **File Security** | Only PDF/DOCX, 10 MB limit, sanitized filenames |
| **Role Protection** | Students can't access faculty routes and vice versa |
| **Error Handling** | Generic error messages — no stack traces exposed |
| **Activity Logging** | Failed logins and suspicious activity logged to `app.log` |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Flask** | Backend web framework |
| **MongoDB Atlas** | Cloud database (users, assignments, submissions) |
| **HTML / CSS / Bootstrap 5** | Frontend UI |
| **Scikit-learn** | TF-IDF Vectorizer + Cosine Similarity |
| **PyPDF2** | PDF text extraction |
| **python-docx** | DOCX text extraction |
| **Flask-Limiter** | Rate limiting protection |
| **python-dotenv** | Environment variable management |
| **Gemini API** *(optional)* | AI-based similarity explanation |

---

## 📁 Project Structure

```
AI-Assignment-Plagiarism-Checker/
├── app.py                        # Main Flask application
├── db.py                         # MongoDB connection setup
├── .env                          # Secrets (git-ignored)
├── .gitignore                    # Ignored files
├── requirements.txt              # Python dependencies
├── utils/
│   ├── text_extractor.py         # PDF/DOCX text extraction
│   └── similarity.py             # TF-IDF similarity engine
├── templates/
│   ├── base.html                 # Common layout (Bootstrap)
│   ├── index.html                # Homepage
│   ├── login.html                # Login page
│   ├── register.html             # Registration page
│   ├── student_dashboard.html    # Student view
│   ├── upload.html               # File upload form
│   ├── faculty_dashboard.html    # Faculty view
│   ├── create_assignment.html    # Create assignment form
│   └── submissions.html          # Plagiarism results table
├── static/
│   └── style.css                 # Custom styles
└── uploads/                      # Uploaded files (git-ignored)
```

---

## ⚙️ Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Assignment-Plagiarism-Checker.git
cd AI-Assignment-Plagiarism-Checker
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` File

Create a file named `.env` in the project root with the following content:

```
MONGO_URI=your_mongodb_connection_string_here
SECRET_KEY=your_flask_secret_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

> ⚠️ **Never share or commit this file.** It is already listed in `.gitignore`.

### 4. Setup MongoDB

- Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Get your connection string and paste it in `.env` as `MONGO_URI`

---

## 🚀 How to Run

```bash
python app.py
```

Or using Flask CLI:

```bash
python -m flask run
```

Open your browser and go to: **http://127.0.0.1:5000**

---

## 📸 Screenshots

| Page | Preview |
|------|---------|
| Homepage | *Add screenshot here* |
| Student Dashboard | *Add screenshot here* |
| Faculty Dashboard | *Add screenshot here* |
| Plagiarism Results | *Add screenshot here* |

---

## 🔮 Future Improvements

- 🔐 Password hashing (bcrypt)
- 🤖 Gemini AI-powered similarity explanations
- 📊 Detailed plagiarism reports with highlighted text
- 📧 Email notifications for high plagiarism alerts
- 📱 Responsive mobile-friendly design
- 📥 Bulk assignment upload support
- 📈 Analytics dashboard for faculty

---

## 👤 Author

**Divyansh Tikka**

---

## 📄 License

This project is for educational purposes.
