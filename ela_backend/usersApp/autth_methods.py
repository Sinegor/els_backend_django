import os
import dotenv
import smtplib

from dotenv import load_dotenv
from email.message import EmailMessage
from os import getenv

from usersApp.models import FieldsOfLaw
load_dotenv()


def push_auth_email(email, name):
    SMT_LOGIN = getenv ("SMT_LOGIN")
    SMT_PASS = getenv ('SMT_PASS')
    text = f'{name} для окончания регистрации вам необходимо пройти по ссылке: "http://127.0.0.1:8000/accounts/registration/starting/{name}"'
    auth_msg = EmailMessage()
    auth_msg['Subject'] = 'confirmation of registration:' 
    auth_msg['From'] = SMT_LOGIN
    auth_msg['To'] = email
    auth_msg.set_content(text)
    with smtplib.SMTP(host='smtp.gmail.com', port='587') as s:
        s.starttls()
        s.login(SMT_LOGIN, SMT_PASS)
        s.send_message(auth_msg)

