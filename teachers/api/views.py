from rest_framework import permissions, viewsets

from students.api.utils import UserDestroyMixin, UserUpdateMixin
from teachers.api.serializers import (
    ClassSerializer,
    SubjectSerializer,
    TeacherSerializer,
)
from teachers.models import Class, Subject, Teacher


class TeacherViewSet(
    UserUpdateMixin, UserDestroyMixin, viewsets.ModelViewSet
):
    """
    A view class for handling Teacher objects.

    This view class handles the CRUD operations for Teacher objects.
    """

    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = "__all__"

    def get_queryset(self):
        """
        Returns the queryset of teachers based on the user's authentication and role.

        Returns:
            queryset: The queryset of teachers.
        """
        user = self.request.user
        queryset = Teacher.objects.all()

        if user.is_authenticated:
            if user.is_superuser:
                return queryset

            if user.institution:
                return queryset.filter(
                    user__institution_id=user.institution.id
                )

        return queryset.none()

    def get_serializer_context(self):
        return {"request": self.request}


class ClassViewSet(viewsets.ModelViewSet):
    """
    A view class for handling Class objects.

    This view class handles the CRUD operations for Class objects.
    """

    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = "__all__"

    def get_queryset(self):
        """
        Returns the queryset of classes based on the user's authentication and
        role.

        Returns:
            queryset: The queryset of classes.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return Class.objects.all()

            if user.institution:
                return Class.objects.filter(
                    teacher__user__institution_id=user.institution.id
                )

        return Class.objects.none()

    def get_serializer_context(self):
        return {"request": self.request}


class SubjectViewSet(viewsets.ModelViewSet):
    """
    A view class for handling Subject objects.

    This view class handles the CRUD operations for Subject objects.
    """

    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = "__all__"

    def get_queryset(self):
        """
        Returns the queryset of subjects based on the user's authentication
        and role.

        Returns:
            queryset: The queryset of subjects.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return Subject.objects.all()

            if user.institution:
                return Subject.objects.filter(
                    teacher__user__institution_id=user.institution.id
                )

            return Subject.objects.none()

    def get_serializer_context(self):
        return {"request": self.request}
