import smtplib
# from .forget_password import 
from email.message import EmailMessage
import os
from dotenv import loadenv



loadenv() 

email = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")
port = os.getenv("PORT")


def send_email(recipient, subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = recipient
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", port) as smtp:
            smtp.login(email,password)
            smtp.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")