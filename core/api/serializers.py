from rest_framework import serializers

from core.api.validators import (
    InstitutionValidationMixin,
    UserCreationInstitutionValidationMixin,
)
from core.models import Institution, User


class UserSerializer(
    UserCreationInstitutionValidationMixin, serializers.ModelSerializer
):
    url = serializers.HyperlinkedIdentityField(
        view_name="core-api:user-detail"
    )

    class Meta:
        model = User
        fields = [
            "url",
            "username",
            "first_name",
            "last_name",
            "fullname",
            "email",
            "date_of_birth",
            "address",
            "sex",
            "phone_number",
            "role",
            "institution",
        ]

        read_only_fields = ["url", "fullname"]


class InstitutionSerializer(
    InstitutionValidationMixin, serializers.ModelSerializer
):
    url = serializers.HyperlinkedIdentityField(
        view_name="core-api:institution-detail"
    )

    class Meta:
        model = Institution
        fields = "__all__"
