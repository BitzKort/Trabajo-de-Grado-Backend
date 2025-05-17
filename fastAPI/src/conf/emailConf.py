from fastapi_mail import ConnectionConfig
import dotenv
import os

dotenv.load_dotenv("../.env.dev")

EMAIL= os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

conf = ConnectionConfig(
    MAIL_USERNAME   = EMAIL,
    MAIL_PASSWORD   = EMAIL_PASSWORD,
    MAIL_FROM       = EMAIL,
    MAIL_PORT       = 587,
    MAIL_SERVER     = "smtp.gmail.com",
    MAIL_STARTTLS   = True,   
    MAIL_SSL_TLS    = False,   
    USE_CREDENTIALS = True,
    VALIDATE_CERTS  = True,
)