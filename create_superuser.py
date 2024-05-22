#!/usr/bin/env python
"""This script is used to create a superuser for the application."""

import os
import django

from core.models import User
from dotenv import load_dotenv

load_dotenv()


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduverse.settings")
django.setup()


User.objects.create_superuser(
    username="eduverse-admin",
    email=os.environ.get("EMAIL_USER"),
    password="adminP@$$_",
    first_name="Eduverse",
    last_name="Admin",
)
