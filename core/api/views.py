import os

import yaml
from django.http import HttpResponse
from django.views import View
from rest_framework import viewsets

from core.api.permissions import IsOwnerOrAdmin, IsSuperAdminOrAdmin
from core.api.serializers import InstitutionSerializer, UserSerializer
from core.models import Institution, User


class APISchemaView(View):
    """
    A view class for retrieving the API schema.

    This view class handles the GET request and returns the API schema in YAML format.

    Methods:
        get(request, *args, **kwargs): Retrieves the API schema and returns it as a YAML response.
    """

    def get(self, request, *args, **kwargs):
        with open(os.environ.get("API_SCHEMA"), "r") as file:
            schema = yaml.safe_load(file)
        return HttpResponse(
            yaml.dump(schema), content_type="application/vnd.oai.openapi"
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    A view class for handling User objects.

    This view class handles the CRUD operations for User objects.
    """

    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]
    filterset_fields = [
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
    search_fields = ["username", "email"]
    ordering_fields = ["username", "role"]

    def get_queryset(self):
        """
        Returns the queryset of users based on the user's authentication and
        role.

        Returns:
            queryset: The queryset of users.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return User.objects.all()

            if user.institution:
                # Return all users in the institution that the user belongs to
                return User.objects.filter(institution_id=user.institution_id)

            # for users who are not superusers and do not belong to any
            # institution return only their user object
            return User.objects.filter(pk=user.pk)


class InstitutionViewSet(viewsets.ModelViewSet):
    """
    A view class for handling Institution objects.

    This view class handles the CRUD operations for Institution objects.
    """

    serializer_class = InstitutionSerializer
    permission_classes = [IsSuperAdminOrAdmin]
    filterset_fields = "__all__"

    def get_queryset(self):
        """
        Returns the queryset of institutions based on the user's
        authentication and role.

        Returns:
            queryset: The queryset of institutions.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return Institution.objects.all()

            if user.institution_id:
                return Institution.objects.filter(id=user.institution_id)

            return Institution.objects.none()

    def get_serializer_context(self):
        return {"request": self.request}
