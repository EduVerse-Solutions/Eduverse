from rest_framework import permissions, viewsets

from students.api.serializers import GuardianSerializer, StudentSerializer
from students.api.utils import (
    UserCreateMixin,
    UserDestroyMixin,
    UserUpdateMixin,
)
from students.models import Guardian, Student


class BaseViewSet(
    UserCreateMixin,
    UserUpdateMixin,
    UserDestroyMixin,
    viewsets.ModelViewSet,
):
    pass


class StudentViewSet(BaseViewSet):
    """
    A view class for handling Student objects.

    This view class handles the CRUD operations for Student objects.
    """

    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = "__all__"

    def get_queryset(self):
        """
        Returns the queryset of students based on the user's authentication
        and role.

        Returns:
            queryset: The queryset of students.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return Student.objects.all()

            if user.institution:
                return Student.objects.filter(
                    user__institution_id=user.institution.id
                )

            return Student.objects.none()

    def get_serializer_context(self):
        return {"request": self.request}


class GuardianViewSet(BaseViewSet):
    """
    A view class for handling Guardian objects.

    This view class handles the CRUD operations for Guardian objects.
    """

    serializer_class = GuardianSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returns the queryset of guardians based on the user's role and institution.

        If the user is a superuser, it returns all Guardian objects.
        If the user is not a superuser, it returns Guardian objects with the
        same institution as the user.

        Returns:
            QuerySet: The queryset of guardians.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return Guardian.objects.all()

            if user.institution:
                return Guardian.objects.filter(
                    user__institution_id=user.institution_id,
                    user__role="Guardian",
                )

            return Guardian.objects.none()
