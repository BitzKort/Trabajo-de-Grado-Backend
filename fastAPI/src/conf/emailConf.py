import dotenv
import os
from fastapi_mail import ConnectionConfig


dotenv.load_dotenv("../.env.dev")

EMAIL= os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


"""
    Configuración para el envío del email.

    NOTA
    -------
    Al no estar desplegada la aplicación, usualmente el correo llegará a spam.

"""

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