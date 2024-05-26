"""
This module contains data used for generating dummy data for testing
purposes
"""

import random

from faker import Faker
from phonenumber_field.phonenumber import PhoneNumber

fake = Faker()


def generate_phone_number() -> PhoneNumber:
    """
    Generates a random phone number.

    Returns:
        PhoneNumber: A random phone number.
    """
    phone_number = PhoneNumber.from_string(
        f"+1{random.randint(2000000000, 9999999999)}"  # nosec
    )

    while not phone_number.is_valid():
        phone_number = generate_phone_number()

    return phone_number


user_list = [
    {
        "username": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": "user1@example.com",
        "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=100),
        "address": fake.address(),
        "sex": random.choice(["M", "F"]),  # nosec
        "role": "Super Admin",
        "phone_number": generate_phone_number(),
    },
    {
        "username": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": "user2@example.com",
        "date_of_birth": fake.date_of_birth(minimum_age=5, maximum_age=50),
        "address": fake.address(),
        "sex": random.choice(["M", "F"]),  # nosec
        "role": "Student",
        "phone_number": generate_phone_number(),
    },
    {
        "username": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": "user3@example.com",
        "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=100),
        "address": fake.address(),
        "sex": random.choice(["M", "F"]),  # nosec
        "role": "Guardian",
        "phone_number": generate_phone_number(),
    },
]

institution_list = [
    {
        "name": fake.company(),
        "phone_number": generate_phone_number(),
        "address": fake.address(),
        "email": fake.email(),
    },
    {
        "name": fake.company(),
        "phone_number": generate_phone_number(),
        "address": fake.address(),
        "email": fake.email(),
    },
    {
        "name": fake.company(),
        "phone_number": generate_phone_number(),
        "address": fake.address(),
        "email": fake.email(),
    },
    {
        "name": fake.company(),
        "phone_number": generate_phone_number(),
        "address": fake.address(),
        "email": fake.email(),
    },
    {
        "name": fake.company(),
        "phone_number": generate_phone_number(),
        "address": fake.address(),
        "email": fake.email(),
    },
]
