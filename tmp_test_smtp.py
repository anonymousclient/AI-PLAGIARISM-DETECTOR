import os
from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME")
mail = Mail(app)

def test_email():
    with app.app_context():
        try:
            msg = Message("Test Connection", recipients=[app.config["MAIL_USERNAME"]], body="Testing SMTP connection.")
            mail.send(msg)
            print("SUCCESS: Email sent!")
        except Exception as e:
            print(f"FAILED: {e}")

if __name__ == "__main__":
    test_email()
