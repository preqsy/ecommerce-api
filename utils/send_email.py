import smtplib, ssl
from core import settings

PORT = 465
SMTP_SERVER = "smtp.gmail.com"


def send_email(receiver_email, otp):
    subject = f"Subject: Your One-Time Password (OTP) for FlashFeed"
    body = f"""Hello,

    We hope this message finds you well. As part of our ongoing commitment to ensuring the security of your account, we have generated a one-time password (OTP) for you to use with your FlashFeed account.

    Your OTP: {otp}

    Please use this OTP within the next 5 minutes to complete your authentication process. For security reasons, please do not share this OTP with anyone.

    If you did not request this OTP or have any concerns about the security of your account, please contact our support team immediately at [Support Email Address] or visit our website for assistance.

    Thank you for choosing FlashFeed!"""

    message = f"Subject: {subject}\n\n{body}"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, PORT, context=context) as server:
        server.login(settings.SENDER_EMAIL, settings.SECRET_GMAIL_KEY)
        server.sendmail(
            settings.SENDER_EMAIL, receiver_email, message.encode("ascii", "ignore")
        )
