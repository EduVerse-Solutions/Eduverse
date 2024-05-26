from rest_framework import serializers

from core.models import Institution, User


class UserCreationInstitutionValidationMixin:
    """
    A mixin class for validating institution-related data.

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

        user_data = data.pop("user", data)

        if user_data is None:
            raise serializers.ValidationError("No user data was provided.")

        new_user = User(**user_data)

        if request.method == "POST":
            if not request_user.institution:
                raise serializers.ValidationError(
                    {
                        "institution": "You must belong to an institution to "
                        "perform this action.",
                    },
                    "does_not_have_institution",
                )

            if not new_user.institution:
                raise serializers.ValidationError(
                    {"institution": "The institution field cannot be empty."},
                    "required",
                )

            if request_user.role not in ["Admin", "Super Admin"]:
                raise serializers.ValidationError(
                    {
                        "institution": "You must be an admin to create a user.",
                    },
                    "invalid_role",
                )

        if request.method in ["PUT", "PATCH", "DELETE"]:
            if not request_user.institution:
                raise serializers.ValidationError(
                    {
                        "institution": "You must belong to create an "
                        "institution to perform this action.",
                    }
                )
            if request.method in ["PATCH"]:
                # in case of a patch, let's ensure the user already exists and
                # then update their data with their existing one before
                # proceeding to the partial update
                user = self.context.get("user")
                if not user:
                    pk = request.parser_context.get("kwargs").get("pk")
                    user = User.objects.get(
                        pk=pk, institution_id=request_user.institution.id
                    )
                new_user.__dict__.update(user.__dict__)

            if not (
                request.user.is_superuser
                or new_user.institution == request.user.institution
            ):
                # no one should be able to modify the details of other users
                # from another institution
                raise serializers.ValidationError(
                    {"institution": "Invalid operation, user not found."},
                    "invalid_institution",
                )

            if not Institution.objects.filter(
                id=new_user.institution.id
            ).exists():
                raise serializers.ValidationError(
                    {
                        "institution": "The institution does not exist.",
                    },
                    "invalid_institution",
                )
        return data


class InstitutionValidationMixin:
    def validate(self, data):
        request = self.context.get("request")
        request_user = request.user
        new_institution = Institution(**data)

        if request.method == "POST":
            if request_user.institution:
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
