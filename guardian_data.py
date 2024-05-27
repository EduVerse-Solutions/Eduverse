# noqa: B311
#!/usr/bin/env python

import json
import random
import string

data = {
    "user": {
        "username": "".join(
            random.choices(string.ascii_lowercase, k=8)  # nosec
        ),
        "first_name": "".join(
            random.choices(string.ascii_lowercase, k=8)  # nosec
        ),
        "last_name": "".join(
            random.choices(string.ascii_lowercase, k=8)  # nosec
        ),
        "email": "".join(random.choices(string.ascii_lowercase, k=8))  # nosec
        + "@example.com",
        "date_of_birth": "2019-08-24",
        "address": "".join(
            random.choices(string.ascii_lowercase, k=8)  # nosec
        ),
        "sex": random.choice(["M", "F"]),  # nosec
        "phone_number": "".join(random.choices(string.digits, k=10)),  # nosec
        "institution": random.randint(1, 100),  # nosec
    },
    "wards": [random.randint(1, 100)],  # nosec
    "profession": "".join(
        random.choices(string.ascii_lowercase, k=8)  # nosec
    ),
}

guardians = [data.copy() for _ in range(4)]

with open("guardian.json", "w") as file:
    json.dump(guardians, file, indent=4)
