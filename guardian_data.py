#!/usr/bin/env python
import json
import random

from faker import Faker

fake = Faker()


def generate_guardian_data(count=5):
    data = []

    for _ in range(count):

        user = {
            "username": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "date_of_birth": fake.date_of_birth().strftime("%Y-%m-%d"),
            "address": fake.address(),
            "sex": random.choice(["M", "F"]),  # nosec
            "institution": 0,  # nosec
        }
        wards = []
        profession = fake.job()
        relationship = (
            random.choice(["Father", "Mother", "Guardian"]),  # nosec
        )

        data.append(
            {
                "user": user,
                "wards": wards,
                "profession": profession,
                "relationship": relationship[0],
            }
        )

    with open("guardian.json", "w") as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    generate_guardian_data()
