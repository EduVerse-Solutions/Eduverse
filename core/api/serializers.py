from enum import Enum

from rest_framework import serializers

from core.api.validators import (
    InstitutionValidationMixin,
    UserValidationMixin,
)
from core.models import Institution, InstitutionProfile, User, UserProfile


class Role(str, Enum):
    Student = "Student"
    Teacher = "Teacher"
    Admin = "Admin"
    Guardian = "Guardian"
    SuperAdmin = "Super Admin"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class InstitutionRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        if "request" not in self.context:
            return Institution.objects.none()

        request = self.context["request"]

        if request.user.is_superuser:
            return Institution.objects.all()

        return Institution.objects.filter(owner__pk=request.user.pk)


class RoleBasedOnRoute(serializers.ChoiceField):
    def __init__(self, **kwargs):
        kwargs["choices"] = []
        super().__init__(**kwargs)

    def bind(self, field_name, parent):
        super().bind(field_name, parent)

        request = self.context.get("request")
        if request is None:
            return

        path_role_map = {
            "/api/students": [Role.Student.value],
            "/api/teachers": [Role.Teacher.value],
            "/api/guardians": [Role.Guardian.value],
        }
        path = request.path
        for path_prefix, role in path_role_map.items():
            if path.startswith(path_prefix):
                self.choices = role
                break
        else:
            self.choices = Role.choices()

    def get_choices(self, cutoff=None):
        if "request" in self.context:
            return super().get_choices(cutoff)
        return dict(Role.choices())


class UserSerializer(UserValidationMixin, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="core-api:user-detail"
    )

    institution = InstitutionRelatedField()
    role = RoleBasedOnRoute(required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "url",
            "created_at",
            "updated_at",
            "username",
            "first_name",
            "last_name",
            "fullname",
            "email",
            "date_of_birth",
            "address",
            "sex",
            "phone_number",
            "institution",
            "role",
        ]

        read_only_fields = [
            "url",
            "id",
            "fullname",
            "created_at",
            "updated_at",
        ]


class OwnerRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        if "request" not in self.context:
            return User.objects.none()

        request = self.context["request"]

        if request.user.is_superuser:
            return User.objects.all()

        return User.objects.filter(pk=request.user.pk)


class InstitutionSerializer(
    InstitutionValidationMixin, serializers.ModelSerializer
):
    url = serializers.HyperlinkedIdentityField(
        view_name="core-api:institution-detail"
    )

    owner = OwnerRelatedField()

    class Meta:
        model = Institution
        fields = "__all__"
        read_only_fields = ["id"]


class UserSerializerWithoutInstitution(UserSerializer):
    class Meta(UserSerializer.Meta):
        new_fields = list(UserSerializer.Meta.fields)
        new_fields.remove("institution")
        fields = new_fields


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializerWithoutInstitution()

    class Meta:
        model = UserProfile
        fields = ["user", "bio", "avatar"]


class InstitutionProfileSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer()

    class Meta:
        model = InstitutionProfile
        fields = ["institution", "description", "logo"]
