#!/usr/bin/env python3

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from core.validators import Validators


class User(AbstractUser):
    """
    Represents a user in the system.

    Inherits from the AbstractUser model provided by Django's authentication framework.
    """

    ROLES = [
        ("Super Admin", "Super Admin"),
        ("Admin", "Admin"),
        ("Teacher", "Teacher"),
        ("Student", "Student"),
        ("Guardian", "Guardian"),
        ("Librarian", "Librarian"),
        ("Accountant", "Accountant"),
    ]

    SEX = [("M", "Male"), ("F", "Female")]

    username = models.CharField(
        max_length=20, null=False, blank=False, unique=True
    )
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    fullname = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    date_of_birth = models.DateField(null=False, blank=False)
    address = models.CharField(max_length=255, null=True)
    sex = models.CharField(
        max_length=10, choices=SEX, null=False, blank=False
    )
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default="Super Admin",
        null=False,
        blank=False,
    )
    institution = models.ForeignKey(
        "Institution", on_delete=models.CASCADE, null=True
    )

    def __str__(self) -> str:
        """
        Returns a string representation of the user.

        The string consists of the username and the role of the user.
        """
        return f"{self.username} - {self.role}"

    def save(self, *args, **kwargs):
        """
        Saves the user instance.

        Performs additional operations before saving the user, such as running
        validators, formatting the role and sex fields, and generating the
        fullname field.
        """
        Validators.run_validators(user=self)
        self.role = self.role.title()
        if self.sex:
            self.sex = self.sex.capitalize()

        self.clean()
        self.fullname = f"{self.first_name.strip()} {self.last_name.strip()}"
        self.fullname = self.fullname.title()

        super().save(*args, **kwargs)

    def get_roles(self):
        """
        Returns the list of available roles.

        Each role is represented as a string.
        """
        return [role[0] for role in self.ROLES]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "sex"]

    class Meta:
        ordering = ["id"]


class Institution(models.Model):
    """Institution model."""

    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=100, null=False, blank=False)
    phone_number = PhoneNumberField(null=True, unique=True)
    email = models.EmailField(unique=True, null=False)
    owner = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="owner",
        null=False,
        blank=False,
    )
    website = models.URLField(null=True, blank=True)
    tagline = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        Validators.run_validators(user=self.owner, institution=self)
        super().save(*args, **kwargs)
