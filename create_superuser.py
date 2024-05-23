#!/usr/bin/env python
"""This script is used to create a superuser for the application."""

# flake8: noqa: E402

import os
from datetime import datetime, timedelta

import django
from django.core.mail import send_mail
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduverse.settings")
django.setup()

from rest_framework.authtoken.models import Token

from core.models import User

# trunk-ignore(bandit/B106)
user = User.objects.create_superuser(
    username="eduverse-admin",
    email=os.environ.get("EMAIL_USER"),
    password="adminP@$$_",
    first_name="EduVerse",
    last_name="Admin",
    sex="F",
    role="Super Admin",
    date_of_birth=datetime.now() - timedelta(days=365 * 25),
)

# after creating the user, let's send them their token through email
token = Token.objects.get(user=user)

print("Sending token, please check your email...")
send_mail(
    subject="Token for EduVerse REST API access",
    message=(
        f"Hello {user.username}\n\n"
        f"Here is your token for accessing the EduVerse REST API: {token}"
    ),
    from_email=os.environ.get("EMAIL_USER"),
    recipient_list=[user.email],
    fail_silently=False,
)
