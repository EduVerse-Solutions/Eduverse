#!/usr/bin/env python3

"""Validators for the core app."""

import datetime

from django.core.exceptions import ValidationError

import core.models as models


class Validators:
    """
    A collection of static methods for validating user inputs.
    """

    @staticmethod
    def run_validators(
        user: "models.User" = None,
        institution: "models.Institution" = None,
        user_admin=None,
    ):
        """
        Runs the validators for the given objects.

        Args:
            user: The user object to validate
            institution: The institution object to validate

        Raises:
            ValidationError: If any validation fails.
        """
        if user:
            if isinstance(user, models.User):
                user = user
            elif isinstance(user, dict):
                user = models.User(**user)
            else:
                raise ValueError(
                    "user must be a User instance or a dictionary"
                )

            Validators.validate_sex(user.sex)
            Validators.validate_role(user.role)
            Validators.validate_name_fields(user.first_name, user.last_name)
            Validators.validate_date_of_birth(user.date_of_birth)

        # Add similar checks for institution if needed
        if institution:
            if isinstance(institution, models.Institution):
                institution = institution
            elif isinstance(institution, dict):
                institution = models.Institution(**institution)
            else:
                raise ValueError(
                    "institution must be an Institution instance or a "
                    "dictionary"
                )

            Validators.validate_user_is_owner(
                user=user,
                institution=institution,
                user_admin=user_admin or None,
            )
            Validators.validate_institution_creator(
                user=user, user_admin=user_admin
            )

            if user.role == "Super Admin":
                if isinstance(user.date_of_birth, str):
                    year = datetime.datetime.fromisoformat(
                        user.date_of_birth
                    ).year
                else:
                    year = user.date_of_birth.year
                if datetime.datetime.now().year - year < 18:
                    print(user)
                    print(user.date_of_birth)
                    raise (
                        ValidationError(
                            "You must be at least 18 years old to create "
                            "an institution."
                        )
                    )

    @staticmethod
    def validate_date_of_birth(date_of_birth: str | datetime.date):
        """
        Validates the date of birth.

        Args:
            date_of_birth (str): The date of birth to be validated.

        Raises:
            ValidationError: If the date of birth is not in the correct format.
        """
        if date_of_birth is None:
            raise ValidationError("Date of birth must not be empty.")

        if isinstance(date_of_birth, datetime.date):
            date_of_birth = date_of_birth.strftime("%Y-%m-%d")

        try:
            date_of_birth = date_of_birth.split("-")
            if len(date_of_birth) != 3:
                raise ValueError
            year, month, day = date_of_birth
            if len(year) != 4 or len(month) != 2 or len(day) != 2:
                raise ValueError
            year, month, day = int(year), int(month), int(day)
            if month < 1 or month > 12 or day < 1 or day > 31:
                raise ValueError
        except ValueError as err:
            raise ValidationError(
                "Date of birth must be in the format 'YYYY-MM-DD'."
            ) from err

    @staticmethod
    def validate_name_fields(first_name: str, last_name: str):
        """
        Validates the first name and last name fields.

        Args:
            first_name (str): The first name to be validated.
            last_name (str): The last name to be validated.

        Raises:
            ValueError: If the first name or last name is empty.
        """
        if not first_name or not last_name:
            raise ValidationError(
                "First name and last name must not be empty."
            )

        if not all(word.isalpha() for word in first_name.split()) or not all(
            word.isalpha() for word in last_name.split()
        ):
            raise ValidationError(
                "First name and last name must contain only alphabets."
            )

        if len(first_name) < 2 or len(last_name) < 2:
            raise ValidationError(
                "First name and last name must be at least 2 characters long."
            )

    @staticmethod
    def validate_sex(sex: str):
        """
        Validates the given sex.

        Args:
            sex (str): The sex to be validated.

        Raises:
            ValidationError: If the sex is not 'M' or 'F'.
        """
        if sex.capitalize() not in ["M", "F"]:
            raise ValidationError(f"Invalid sex: {sex}. Must be 'M' or 'F'.")

    @staticmethod
    def validate_role(role: str):
        """
        Validates the given role.

        Args:
            role (str): The role to be validated.

        Raises:
            ValidationError: If the role is not valid.
        """
        roles = models.User().get_roles()
        if role not in roles:
            raise ValidationError(
                f"Invalid role: {role}.\nList of roles: {roles}"
            )

    @staticmethod
    def validate_institution(institution: "models.Institution"):
        """
        Validates the given institution.

        Args:
            institution (models.Institution): The institution object.

        Raises:
            ValidationError: If the institution is not valid.
        """
        if institution.owner.role != "Super Admin":
            raise ValidationError(
                "Only a Super Admin can create an institution."
            )

    @staticmethod
    def validate_user_belongs_to_institution(
        user: "models.User", institution: "models.Institution"
    ):
        """
        Validates that the given user belongs to an institution.

        This validation ensures that a user can perform actions only in the
        institution they belong to. Also, certain actions are prevented unless
        the user belongs to an institution. In the case of the Owner of an
        institution, they must create an institution first before they are
        able to create other entities like Students, Teachers, etc.
        For good measure, this also restricts zombie users from doing anything
        until they belong to an institution where they will be governed.

        Args:
            user (models.User): The user object.
            institution (models.Institution): The institution object.

        Raises:
            ValidationError: If the user does not belong to the institution or
            is not the owner.
        """
        if user:
            if isinstance(user, models.User):
                user = user
            elif isinstance(user, dict):
                user = models.User(**user)
            else:
                raise ValueError(
                    "user must be a User instance or a dictionary"
                )

            if user.institution is None:
                raise ValidationError(
                    "User must belong to an institution to perform this action."
                )

        if institution:
            if isinstance(institution, models.Institution):
                institution = institution
            elif isinstance(institution, dict):
                institution = models.Institution(**institution)
            else:
                raise ValueError(
                    "institution must be an Institution instance or a "
                    "dictionary"
                )

            if user.institution != institution:
                raise ValidationError(
                    "You don't have the permissions to perform this action."
                )

    @staticmethod
    def validate_user_is_owner(
        user: "models.User",
        institution: "models.Institution",
        user_admin=None,
    ):
        """
        Validates that the given user is the owner of the institution.

        Args:
            user (models.User): The user object.
            institution (models.Institution): The institution object.

        Raises:
            ValidationError: If the user is not the owner of the institution.
        """
        if user_admin:
            user = user_admin

        if user != institution.owner:
            raise ValidationError(
                "Only the owner of the institution can perform this action."
            )

    @staticmethod
    def validate_institution_creator(user: "models.User", user_admin=None):
        """
        Validates that the entity trying to create an institution on the
        platform has the privileges to do so.
        In this project, the user must be a Super Admin (privilege for the
        owner of an institution)
        """
        if user_admin:
            user = user_admin

        if user.role != "Super Admin":
            raise ValidationError(
                "You are not permitted to perform this action."
            )

        if datetime.datetime.now().year - user.date_of_birth.year < 18:
            raise ValidationError(
                "User must be at least 18 years old to perform this action."
            )
