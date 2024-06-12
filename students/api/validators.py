"""
This module contains validations for API requests for the Student and
Guardian endpoints. It ensures that the date is valid before sending it to the
database for it to be saved
"""

from datetime import date

from rest_framework import serializers

from core.models import Institution, User
from students.models import Guardian, Student
from teachers.models import Class, Teacher


class BaseValidationMixin:
    """
    Mixin class for validating data in serializers.

    This mixin provides common validation logic for serializers.
    It checks if the request is available in the serializer context,
    validates the provided data, and performs additional checks based on
    the user's role and permissions.

    Attributes:
        model_name (str): The name of the model being validated.
    """

    def validate(self, data):
        request = self.context.get("request")
        if request is None:
            raise serializers.ValidationError(
                {
                    f"{self.model_name}": "Request is not available in the "
                    "serializer context."
                }
            )

        request.user = request.user
        if (
            Teacher.objects.filter(
                user__institution=request.user.institution
            ).count()
            == 0
        ):
            raise serializers.ValidationError(
                {
                    f"{self.model_name}": "You can't create "
                    f"{self.model_name}s without a teacher. "
                    "Create one first and try again."
                }
            )

        if (
            Class.objects.filter(
                teacher__user__institution=request.user.institution
            ).count()
            == 0
        ):
            raise serializers.ValidationError(
                {
                    f"{self.model_name}": "You can't create "
                    f"{self.model_name}s without a class. "
                    "Create one first and try again."
                }
            )

        if data is None:
            raise serializers.ValidationError(
                "No data was provided to the serializer."
            )

        model_data = data.pop(self.model_name, data)

        if model_data is None:
            print("Yep, error")
            raise serializers.ValidationError(
                {
                    f"{self.model_name}_validation": f"No {self.model_name} data was provided."
                }
            )

        user_data = data.get("user", None)
        if user_data is None:
            raise serializers.ValidationError(
                {
                    f"{self.model_name}_validation": "No user data was "
                    "provided."
                }
            )
        user_data["institution"] = request.user.institution
        user = User(**user_data)

        if request.user.is_superuser:
            return data  # the site admin is allowed full control

        if request.method in ["POST", "PUT", "PATCH"]:
            if not (request.user.is_superuser or request.user.institution):
                raise serializers.ValidationError(
                    "Only and users with an institution can create "
                    f"{self.model_name}s."
                )

        if request.user.institution:
            if user.institution != request.user.institution:
                raise serializers.ValidationError(
                    f"You can only create {self.model_name}s in your own "
                    "institution."
                )

        return data


class StudentValidationMixin(BaseValidationMixin):
    """
    Mixin class for validating student data.
    """

    model = Student
    model_name = "student"

    def validate(self, data):
        """
        Validate the student data.

        Args:
            data (dict): The student data to be validated.

        Returns:
            dict: The validated student data.

        Raises:
            serializers.ValidationError: If the validation fails.
        """

        data = super().validate(data)

        request = self.context.get("request")

        if "class_id" not in data and request.method in [
            "POST",
            "PUT",
        ]:
            raise serializers.ValidationError(
                {"class_id": "Class is required."}, code="required"
            )

        student_data = data
        user_data = data.get("user")

        # Set the institution for the user
        if not isinstance(user_data["institution"], Institution):
            user_data["institution"] = Institution.objects.get(
                id=user_data.get("institution")
            )

        # Convert the date of birth to a date object
        if isinstance(user_data["date_of_birth"], str):
            user_data["date_of_birth"] = date.fromisoformat(
                user_data["date_of_birth"]
            )

        # Create a User instance with the user data
        user = User(**user_data)

        # Create a Student instance with the user and student data
        student_data.pop("user", None)
        student = Student(user=user, **student_data)

        # Check if admission number is provided
        if student.admission_number is None:
            raise serializers.ValidationError(
                {"admission_number": "Admission number is required."},
                code="required",
            )

        # Check if the request method is PATCH and the student user is not the
        # same as the request user
        if request.method == "PATCH":
            if (
                student.user != request.user
                and not request.user.is_superuser
                and not (
                    request.user.role in ["Super Admin", "Admin"]
                    and student.user.institution == request.user.institution
                )
            ):
                raise serializers.ValidationError(
                    {
                        "student": "You can only update your own student "
                        "account."
                    }
                )

        # Check if the student belongs to an institution
        if not student.user.institution:
            raise serializers.ValidationError(
                {"student": "A student must belong to an institution."}
            )

        # Check if the date of admission is after the date of birth
        if user.date_of_birth > student.date_of_admission:
            raise serializers.ValidationError(
                {
                    "date_of_admission": "Date of admission cannot be before "
                    "date of birth."
                },
                code="invalid",
            )

        # Check if the date of graduation is before the date of admission
        if student.date_of_graduation:
            if student.date_of_graduation < student.date_of_admission:
                raise serializers.ValidationError(
                    {
                        "date_of_graduation": "Date of graduation cannot be "
                        "before date of admission."
                    },
                    code="invalid",
                )

        if student.guardian:
            if student.guardian.user.institution != student.user.institution:
                raise serializers.ValidationError(
                    {
                        "student": "The guardian must belong to the same "
                        "institution as the student."
                    },
                    code="invalid",
                )

            if (
                student.user.date_of_birth
                > student.guardian.user.date_of_birth
            ):
                raise serializers.ValidationError(
                    {
                        "student": "The guardian cannot be younger than the "
                        "student."
                    }
                )

        data["user"] = user_data
        return data


class GuardianValidationMixin(BaseValidationMixin):
    """
    Mixin class for validating Guardian instances.

    This mixin provides a validate method that performs additional validation
    specific to Guardian instances. It checks if all the wards associated with
    the guardian are instances of the Student model.

    Attributes:
        model (Model): The model class for which the validation is performed.
        model_name (str): The name of the model.

    Methods:
        validate(data): Validates the provided data and returns the validated
        data.
    """

    model = Guardian
    model_name = "guardian"

    def validate(self, data):
        data = super().validate(data)
        user_data = data.get("user")
        guardian = User(**user_data)

        wards = data.get("wards")
        if len(wards) == 0:
            raise serializers.ValidationError(
                {"guardian_wards": "At least one ward is required"},
                code="required",
            )

        if not all(isinstance(ward, Student) for ward in wards):
            raise serializers.ValidationError(
                {"guardian_wards": "All wards must be Student instances"},
                code="invalid",
            )

        if any(
            ward
            for ward in wards
            if ward.user.date_of_birth < guardian.date_of_birth
        ):
            raise serializers.ValidationError(
                {"guardian": "Wards can't be older than guardian"}
            )

        return data
