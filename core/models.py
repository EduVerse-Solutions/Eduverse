#!/usr/bin/env python3

from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image

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

    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    username = models.CharField(
        max_length=20, null=False, blank=False, unique=True
    )
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    fullname = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    date_of_birth = models.DateField(null=False, blank=False)
    address = models.CharField(max_length=255, null=True, blank=True)
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
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        self.fullname = f"{self.first_name.strip()} {self.last_name.strip()}"
        self.fullname = self.fullname.title()

        # before saving, let set all the fields with empty values to None
        for field in self._meta.fields:
            if field.null and field.blank:
                if getattr(self, field.name) == "":
                    setattr(self, field.name, None)

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

    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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


class BaseProfile(models.Model):
    picture_max_width = 500
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)

    def save(self, *args, **kwargs):
        """
        Overrides the save method to resize the logo image before saving.
        """
        super().save(*args, **kwargs)

        if hasattr(self, "avatar"):
            image_field = self.avatar
        elif hasattr(self, "logo"):
            image_field = self.logo
        else:
            return

        img = Image.open(image_field.path)

        if max(img.size) > self.picture_max_width:
            width, height = img.size
            if width > height:
                ratio = self.picture_max_width / width
                new_size = (self.picture_max_width, round(height * ratio))
            else:
                ratio = self.picture_max_width / height
                new_size = (round(width * ratio), self.picture_max_width)
            img = img.resize(new_size, Image.LANCZOS)

        img.save(image_field.path)


class UserProfile(BaseProfile):
    """
    A model representing a user profile.

    Attributes:
        user (User): The user associated with the profile.
        avatar (ImageField): The profile avatar image.
        bio (TextField): The user's biography.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )

    avatar = models.ImageField(
        default="default.png", upload_to="profile_images"
    )
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        """
        Returns a string representation of the profile.

        Returns:
            str: The username of the associated user.
        """
        return f"{self.user.username} - Profile"


class InstitutionProfile(BaseProfile):
    """
    A model representing an institution profile.

    Attributes:
        institution (Institution): The institution associated with the profile.
        logo (ImageField): The institution logo image.
        description (TextField): The institution description.
    """

    institution = models.OneToOneField(
        Institution, on_delete=models.CASCADE, related_name="profile"
    )

    logo = models.ImageField(
        default="default.png", upload_to="institution_images"
    )
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        """
        Returns a string representation of the profile.

        Returns:
            str: The name of the associated institution.
        """
        return f"{self.institution.name} - Profile"
