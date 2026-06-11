# app/infrastructure/email/smtp_service.py
import smtplib
import os
from email.message import EmailMessage

class EmailService:
    def __init__(self):
        # In a real app, these MUST come from your .env file
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER", "your-email@gmail.com") # Replace this
        self.smtp_pass = os.getenv("SMTP_PASS", "your-16-char-app-password") # Replace this

    def send_otp(self, to_email: str, otp_code: str):
        """Builds and sends the OTP email securely."""
        
        # 1. Build the email
        msg = EmailMessage()
        msg['Subject'] = 'Your Workspace Verification Code'
        msg['From'] = self.smtp_user
        msg['To'] = to_email
        
        # 2. Set the email body
        msg.set_content(f"""
        Welcome to the platform!
        
        Your verification code is: {otp_code}
        
        This code will expire in 5 minutes. If you did not request this, please ignore this email.
        """)

        # 3. Connect to the server and send
        try:
            # starttls() encrypts the connection so your password and OTP aren't sent in plain text
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls() 
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
                
            print(f"SUCCESS: Email securely delivered to {to_email}")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to send email: {e}")
            # We don't raise an HTTPException here because we don't want to 
            # crash the registration just because the email was slow.