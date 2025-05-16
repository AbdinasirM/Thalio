from dotenv import load_dotenv
import os
from pathlib import Path

import smtplib
# from .forget_password import 
from email.message import EmailMessage


# Build the full path to the .env file
env_path = Path(__file__).resolve().parent / "forget_email_creds" / ".env"
load_dotenv(dotenv_path=env_path)

email = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")  
port  = int(os.getenv("PORT"))


def send_email(recipient, subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = recipient
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com",int(port)) as smtp:
            smtp.login(email, password)
            smtp.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")