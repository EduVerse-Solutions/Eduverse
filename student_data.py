#!/usr/bin/env python
import json
import random

from faker import Faker

fake = Faker()

data = []

for _ in range(4):
    user = {
        "username": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "date_of_birth": fake.date_of_birth().strftime("%Y-%m-%d"),
        "address": fake.address(),
        "sex": random.choice(["M", "F"]),  # nosec
        "phone_number": fake.phone_number(),
        "institution": random.randint(1, 10),  # nosec
    }

    admission_number = fake.random_int(min=1000, max=9999)
    date_of_admission = fake.date_between(
        start_date="-5y", end_date="today"
    ).strftime("%Y-%m-%d")
    date_of_graduation = fake.date_between(
        start_date="today", end_date="+5y"
    ).strftime("%Y-%m-%d")

    guardian = None

    data.append(
        {
            "user": user,
            "admission_number": str(admission_number),
            "date_of_admission": date_of_admission,
            "date_of_graduation": date_of_graduation,
            "guardian": guardian,
        }
    )

# save it to a file
with open("student_data.json", "w") as f:
    json.dump(data, f, indent=2)
