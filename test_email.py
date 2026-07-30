import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
gmail_address = os.getenv("GMAIL_ADDRESS")
gmail_password = os.getenv("GMAIL_APP_PASSWORD")

if not gmail_address or gmail_address == "your_email@gmail.com":
    print("Please set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env")
    exit(1)

msg = EmailMessage()
msg.set_content("This is a test email from AgentOps Phase 0.")
msg["Subject"] = "AgentOps SMTP Test"
msg["From"] = gmail_address
msg["To"] = gmail_address

try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(gmail_address, gmail_password)
    server.send_message(msg)
    server.quit()
    print("Email sent successfully to", gmail_address)
except Exception as e:
    print("Failed to send email:", e)
