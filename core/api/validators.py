from datetime import date, datetime

from rest_framework import serializers

from core.models import Institution, User
from students.models import Guardian

unneeded_fields = [
    "url",
    "links",
    "count",
    "total_pages",
    "current_page",
    "results",
]


class UserValidationMixin:
    """
    A mixin class for validating user information before passing it to the
    backend for saving.

    This mixin provides validation logic for institution-related data, such as
    checking if the institution field is empty, verifying the user's
    institution, and ensuring that only admins can create users.

    Methods:
        validate(data): Validates the given data based on the request method and
            the user's role and institution.

    Usage:
        This mixin can be used in serializers or views to perform institution
        validation before processing the data.
    """

    def validate(self, data):
        """
        Validates the data for creating or updating a user.

        Args:
            data (dict): The data to be validated.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If the validation fails.
        """
        request = self.context.get("request")
        if request is None:
            raise serializers.ValidationError(
                "Request is not available in the serializer context."
            )

        request_user = request.user

        if data is None:
            raise serializers.ValidationError(
                "No data was provided to the serializer."
            )

        if "view" in request.parser_context:
            view = request.parser_context.get("view")
            response = view.get(request)
            if "guardian" in response.data:
                guardian_id = response.data.get("guardian")
                if guardian_id:
                    response.data["guardian"] = Guardian.objects.get(
                        id=guardian_id
                    )
            user_data = response.data.get("user", response.data)
            if user_data:
                for field in unneeded_fields:
                    user_data.pop(field, None)

        if len(user_data) == 0:
            user_data = data.pop("user", data)

        if user_data is None:
            raise serializers.ValidationError("No user data was provided.")

        if (
            "institution" in user_data
            and user_data.get("institution")
            and not isinstance(user_data.get("institution"), Institution)
        ):
            user_data["institution"] = Institution.objects.get(
                id=user_data["institution"]
            )

        date_of_birth = user_data.get("date_of_birth", None)
        if date_of_birth:
            if not isinstance(date_of_birth, date):
                user_data["date_of_birth"] = date.fromisoformat(date_of_birth)

        new_user = User(**user_data)

        if request.method == "POST":
            if not (request_user.is_superuser or request_user.institution):
                raise serializers.ValidationError(
                    {
                        "user": "You must belong to an institution to "
                        "perform this action.",
                    },
                    "does_not_have_institution",
                )

            if not request_user.is_superuser and not new_user.institution:
                raise serializers.ValidationError(
                    {"user": "The institution field cannot be empty."},
                    "required",
                )

            if request_user.role not in ["Admin", "Super Admin"]:
                raise serializers.ValidationError(
                    {
                        "user": "You must be an admin to create a user.",
                    },
                    "invalid_role",
                )

        if request.method in ["PUT", "PATCH", "DELETE"]:
            if (
                not request_user.is_superuser
                and request_user != new_user
                and request_user.institution != new_user.institution
                and request_user != new_user.institution.owner
            ):
                raise serializers.ValidationError(
                    {
                        "user": "You do not have permission to modify this "
                        "object."
                    },
                    "does_not_have_institution_and_not_admin",
                )

            if not (
                request.user.is_superuser
                or new_user.institution == request.user.institution
            ):
                # no one should be able to modify the details of other users
                # from another institution
                raise serializers.ValidationError(
                    {"user": "Invalid operation, user not found."},
                    "invalid_institution",
                )

        if request_user.is_superuser:
            chk_user = new_user
        else:
            chk_user = request_user

        if chk_user.role == "Super Admin":
            # ensure that Institution owners are at least 18 years old
            if datetime.today().year - chk_user.date_of_birth.year < 18:
                raise serializers.ValidationError(
                    {"user": "Institution owners must be at least 18 years."},
                    "age_restriction",
                )

        if new_user.date_of_birth > date.today():
            raise serializers.ValidationError(
                {"date_of_birth": "Date of birth cannot be in the future."},
                code="invalid",
            )
        new_user.__dict__.update(data)
        return data


class InstitutionValidationMixin:
    def validate(self, data):
        request = self.context.get("request")
        request_user = request.user
        new_institution = Institution(**data)

        if request.method in ["PUT", "POST"]:
            if not new_institution.phone_number:
                raise serializers.ValidationError(
                    {
                        "phone_number": "Phone number is required.",
                    },
                    "required",
                )
        if request.method == "POST":
            if request_user.institution and not request_user.is_superuser:
                raise serializers.ValidationError(
                    {
                        "institution": "You must not belong to an institution "
                        "to perform this action.",
                    },
                    "already_has_institution",
                )

        if request.method in ["PUT"]:
            if not (request_user.institution and request_user.is_superuser):
                raise serializers.ValidationError(
                    {
                        "institution": "You must belong to an institution to "
                        "perform this action.",
                    },
                    "does_not_have_institution",
                )

        if request.method in ["PUT", "PATCH", "DELETE"]:
            if request.method in ["PATCH"]:
                # in case of a patch, let's ensure the institution already
                # exists and then update its data with its existing one before
                # proceeding to the partial update
                if request_user.is_superuser:
                    pk = request.parser_context.get("kwargs").get("pk")
                    institution = Institution.objects.get(pk=pk)
                else:
                    pk = request.parser_context.get("kwargs").get("pk")
                    institution = Institution.objects.get(
                        pk=pk, id=request_user.institution.id
                    )
                new_institution.__dict__.update(institution.__dict__)

            if not (
                request.user.is_superuser
                or new_institution == request.user.institution
            ):
                # no one should be able to modify the details of other
                # institutions from another institution
                raise serializers.ValidationError(
                    {
                        "institution": "You can't perform this action because "
                        "you don't belong to this organization."
                    },
                    "invalid_operation",
                )

            if request_user.role not in ["Admin", "Super Admin"]:
                raise serializers.ValidationError(
                    {
                        "institution": "Only administrators can perform this "
                        "action."
                    },
                    "invalid_role",
                )

        return data
