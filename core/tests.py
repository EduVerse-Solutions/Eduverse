"""This module contains test cases for the core-app."""

from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models import User
from core.validators import Validators


class UserTestCase(TestCase):
    """
    Test case for the User model.
    """

    def setUp(self):
        """
        Set up the test environment by creating a user instance.
        """
        self.user = User.objects.create(
            first_name="Test",
            last_name="User",
            username="testuser",
            email="testuser@email.com",
            role="Super Admin",
            date_of_birth=datetime.now() - timedelta(days=365 * 25),
            sex="M",
        )

    def test_user_creation_details(self):
        """
        Test the user creation details.
        """
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first(), self.user)

    def test_invalid_sex(self):
        """
        Test setting an invalid sex value for the user.
        """
        with self.assertRaises(ValidationError):
            self.user.sex = "invalid"
            self.user.save()

    def test_valid_sex(self):
        """
        Test setting a valid sex value for the user.
        """
        self.user.sex = "F"
        self.assertEqual(self.user.sex, "F")

    def test_invalid_role(self):
        """
        Test setting an invalid role value for the user.
        """
        with self.assertRaises(ValidationError):
            self.user.role = "invalid"
            self.user.save()

    def test_valid_role(self):
        """
        Test setting a valid role value for the user.
        """
        self.user.role = "Teacher"
        self.assertEqual(self.user.role, "Teacher")

    def test_save_without_date_of_birth(self):
        """
        Test setting the date of birth to None and saving. This is similar to
        creating a user without the date of birth
        """
        with self.assertRaises(ValidationError):
            self.user.role = "Teacher"
            self.user.date_of_birth = None
            self.user.save()


class ValidatorsTestCase(TestCase):
    """
    Test case for the Validators class.
    """

    def test_validate_sex(self):
        """
        Test the validate_sex method of the Validators class.
        """
        # Test valid inputs
        Validators.validate_sex("M")
        Validators.validate_sex("F")

        # Test invalid input
        with self.assertRaises(ValidationError):
            Validators.validate_sex("Other")

    def test_validate_role(self):
        """
        Test the validate_role method of the Validators class.
        """
        Validators.validate_role("Admin")

        # Test invalid input
        with self.assertRaises(ValidationError):
            Validators.validate_role("InvalidRole")
