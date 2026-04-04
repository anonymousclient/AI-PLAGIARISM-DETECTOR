# 🛡️ AI Assignment Plagiarism Checker

A web-based plagiarism detection system built with **Flask** and **MongoDB**. Faculty can create assignments, students can upload submissions (PDF/DOCX), and the system automatically detects plagiarism using **TF-IDF similarity analysis**.

---

## 📋 Features

- **Role-Based Authentication** — Separate login for Students and Faculty
- **Class Management** — Faculty can create classes with unique 6-digit codes
- **Multi-Tenant System** — Students only see assignments from classes they've joined
- **Student Dashboard** — Join classes and upload submissions
- **Faculty Dashboard** — Create classes, assignments, and manage submissions
- **File Upload** — Accepts PDF and DOCX files with validation
- **Plagiarism Detection** — TF-IDF + Cosine Similarity comparison engine
- **Color-Coded Reports** — Green (Safe), Yellow (Suspicious), Red (High Plagiarism)

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Flask** | Backend web framework |
| **MongoDB Atlas** | Cloud database (users, assignments, submissions, classes) |
| **HTML / CSS / Bootstrap 5** | Frontend UI |
| **Scikit-learn** | TF-IDF Vectorizer + Cosine Similarity |
| **PyPDF2** | PDF text extraction |
| **python-docx** | DOCX text extraction |
| **python-dotenv** | Environment variable management |

---

## 📁 Project Structure

```
AI-Assignment-Plagiarism-Checker/
├── app.py                        # Main Flask application
├── db.py                         # MongoDB connection setup
├── requirements.txt              # Python dependencies
├── Procfile                      # Deployment config for Render
├── .env.example                  # Template for environment variables
├── utils/
│   ├── text_extractor.py         # PDF/DOCX text extraction
│   └── similarity.py             # TF-IDF similarity engine
├── templates/                    # HTML templates (Dashboards, etc.)
├── static/                       # CSS and assets
└── uploads/                      # Local (ephemeral) storage for uploads
```

---

## ⚙️ Installation Steps

### 1. Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/AI-Assignment-Plagiarism-Checker.git
cd AI-Assignment-Plagiarism-Checker
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root directory and add your credentials:
```env
MONGO_URI=your_mongodb_atlas_uri
SECRET_KEY=your_secret_flask_key
MAIL_USERNAME=your_gmail_address
MAIL_PASSWORD=your_gmail_app_password
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Run Locally
```bash
python app.py
```
Visit: **http://127.0.0.1:10000**

---

## 🚀 Deploying to Render

1.  **Push to GitHub**: Upload your project to a GitHub repository.
2.  **Create Web Service**: In Render dashboard, select **New -> Web Service**.
3.  **Build Settings**:
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `python app.py`
4.  **Environment Variables**: Add the following keys in Render's "Environment" tab:
    - `MONGO_URI`, `SECRET_KEY`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `GEMINI_API_KEY`, `PORT` (set to `10000`).

> [!WARNING]
> **Ephemeral Storage**: Render's local `uploads/` folder is cleared on every restart. For permanent storage, integrate AWS S3 or Cloudinary.

---

## 👤 Author
**Divyansh Tikka**
