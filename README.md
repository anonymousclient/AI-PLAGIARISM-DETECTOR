# 🛡️ AI Assignment Plagiarism Checker

A web-based plagiarism detection system built with **Flask** and **MongoDB**. Faculty can create assignments, students can upload submissions (PDF/DOCX), and the system automatically detects plagiarism using **TF-IDF similarity analysis**.

---

## 📋 Features

- **Role-Based Authentication** — Separate login for Students and Faculty
- **Student Dashboard** — View assignments and upload submissions
- **Faculty Dashboard** — Create assignments and manage submissions
- **File Upload** — Accepts PDF and DOCX files with validation
- **Text Extraction** — Automatically extracts text from uploaded documents
- **Plagiarism Detection** — TF-IDF + Cosine Similarity comparison engine
- **Color-Coded Reports** — Green (Safe), Yellow (Suspicious), Red (High Plagiarism)
- **MongoDB Atlas** — Cloud-based persistent data storage

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
| **Gemini API** *(optional)* | AI-based similarity explanation |

---

## 📁 Project Structure

```
AI-Assignment-Plagiarism-Checker/
├── app.py                        # Main Flask application
├── db.py                         # MongoDB connection setup
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignored files
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

### 3. Setup MongoDB

- Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Get your connection string
- Update the `MONGO_URI` in `db.py` with your connection string

### 4. (Optional) Add Gemini API Key

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

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
