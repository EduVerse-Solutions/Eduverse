from rest_framework import permissions, viewsets

from students.api.serializers import GuardianSerializer, StudentSerializer
from students.api.utils import UserDestroyMixin, UserUpdateMixin
from students.models import Guardian, Student


class StudentViewSet(
    UserUpdateMixin, UserDestroyMixin, viewsets.ModelViewSet
):
    """
    A view class for handling Student objects.

    This view class handles the CRUD operations for Student objects.
    """

    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = "__all__"

    def get_queryset(self):
        """
        Returns the queryset of students based on the user's authentication and role.

        Returns:
            queryset: The queryset of students.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return Student.objects.all()

            return Student.objects.filter(
                user__institution_id=user.institution.id, user__role="Student"
            )

    def get_serializer_context(self):
        return {"request": self.request}


class GuardianViewSet(
    UserUpdateMixin, UserDestroyMixin, viewsets.ModelViewSet
):
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
        If the user is not a superuser, it returns Guardian objects with the same institution as the user.

        Returns:
            QuerySet: The queryset of guardians.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return Guardian.objects.all()

            return Guardian.objects.filter(
                user__institution_id=user.institution_id,
                user__role="Guardian",
            )
