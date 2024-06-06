import os

import yaml
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.permissions import (
    IsOwnerOrAdmin,
    IsPartOfInstitution,
    IsSuperAdminOrAdmin,
)
from core.api.serializers import (
    InstitutionProfileSerializer,
    InstitutionSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from core.models import Institution, InstitutionProfile, User, UserProfile


def get_base_template(role):
    match role:
        case "Super Admin":
            return "core/dashboards/admin_dashboard.html"
        case "Student":
            return "students/student_dashboard.html"
        case "Teacher":
            return "teachers/teacher_dashboard.html"
        case _:
            return "core/dashboards/dashboard_base.html"


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


@method_decorator(cache_page(60 * 60 * 2), name="dispatch")
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


class UserProfileListView(LoginRequiredMixin, APIView):
    """
    A view that returns a list of user profiles.
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "api/user_profile_list.html"
    permission_classes = [IsPartOfInstitution]

    def get(self, request):
        """
        Handles GET requests and returns a list of user profiles.

        If the requesting user is a superuser, all user profiles are returned.
        Otherwise, only user profiles belonging to the requesting user's
        institution are returned.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: A response containing the list of user profiles.
        """
        if request.user.is_superuser:
            queryset = UserProfile.objects.all()
        else:
            queryset = UserProfile.objects.filter(
                user__institution=request.user.institution
            )

        base_template = get_base_template(request.user.role)
        return Response(
            {
                "profiles": queryset,
                "base_dashboard_template": base_template,
                "name": "Manage Users",
            }
        )


class UserProfileDetailView(LoginRequiredMixin, APIView):
    """
    A view for displaying and updating user profiles.

    Attributes:
        renderer_classes (list): List of renderer classes for the view.
        template_name (str): Name of the template used for rendering the view.
        permission_classes (list): List of permission classes for the view.
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "api/user_profile_detail.html"
    permission_classes = [IsPartOfInstitution]

    def get(self, request, pk, format=None):
        """
        Handles GET requests for retrieving a user profile.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): The primary key of the user profile to retrieve.
            format (str, optional): The format of the response data.

        Returns:
            Response: The HTTP response containing the serialized user profile.
        """
        profile = get_object_or_404(UserProfile, pk=pk)

        base_template = get_base_template(profile.user.role)

        serializer = UserProfileSerializer(
            profile, context={"request": request}
        )

        return Response(
            {
                "serializer": serializer,
                "profile": profile,
                "base_dashboard_template": base_template,
                "name": "Profile Update",
            }
        )

    def post(self, request, pk):
        """
        Handles POST requests for updating a user profile.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): The primary key of the user profile to update.

        Returns:
            Response: The HTTP response indicating the success of the update.
        """
        profile = get_object_or_404(UserProfile, pk=pk)
        base_template = get_base_template(profile.user.role)

        data = request.data.copy()
        user_data = {}

        for key in list(data.keys()):
            if key.startswith("user."):
                user_key = key.split(".")[1]
                user_data[user_key] = data.pop(key)[0]

        if not request.user.is_superuser:
            user_data["institution"] = profile.user.institution.pk
            user_data["role"] = profile.user.role

        serializer = UserProfileSerializer(
            profile,
            data=data,
            partial=True,
            context={"request": request},
        )
        user_serializer = UserSerializer(
            profile.user,
            data=user_data,
            partial=True,
            context={"request": request},
        )
        if not serializer.is_valid():

            return Response(
                {
                    "serializer": serializer,
                    "profile": profile,
                    "base_dashboard_template": base_template,
                }
            )

        if not user_serializer.is_valid():
            messages.error(
                request, "Please verify you provided the correct data."
            )

            return Response(
                {
                    "serializer": serializer,
                    "profile": profile,
                    "errors": user_serializer.errors,
                    "base_dashboard_template": base_template,
                }
            )

        user_serializer.save()
        serializer.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("core-api:user-profile-detail", pk=pk)


class InstitutionProfileListView(LoginRequiredMixin, APIView):
    """
    View for listing institution profiles.

    This view requires the user to be logged in and has the permission
    classes set to allow only super admins and admins to access it.

    Attributes:
        renderer_classes (list): List of renderer classes used for rendering
        the response.
        template_name (str): Name of the template used for rendering the HTML
        response.
        permission_classes (list): List of permission classes required to
        access the view.
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "api/institution_profile_list.html"
    permission_classes = [IsSuperAdminOrAdmin]

    def get(self, request):
        """
        Handle GET requests to retrieve the institution profiles.

        If the user is a superuser, all institution profiles are returned.
        Otherwise, only the institution profiles owned by the user are returned.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response object containing the institution profiles.
        """
        if request.user.is_superuser:
            queryset = InstitutionProfile.objects.all()
        else:
            queryset = InstitutionProfile.objects.filter(
                institution__owner=request.user
            )

        return Response({"profiles": queryset})


class InstitutionProfileDetailView(LoginRequiredMixin, APIView):
    """
    View for retrieving and updating an institution profile.

    Inherits from LoginRequiredMixin and APIView.

    Attributes:
        renderer_classes (list): List of renderer classes.
        template_name (str): Name of the template to be rendered.
        permission_classes (list): List of permission classes.

    Methods:
        get(request, pk, format=None): Handles GET requests for retrieving the
        institution profile.
        post(request, pk): Handles POST requests for updating the institution
        profile.
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "api/institution_profile_detail.html"
    permission_classes = [IsSuperAdminOrAdmin]

    def get(self, request, pk, format=None):
        """
        Handles GET requests for retrieving the institution profile.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): The primary key of the institution profile.

        Returns:
            Response: The HTTP response containing the serialized institution profile.
        """
        profile = get_object_or_404(InstitutionProfile, pk=pk)

        serializer = InstitutionProfileSerializer(
            profile, context={"request": request}
        )
        return Response({"serializer": serializer, "profile": profile})

    def post(self, request, pk):
        """
        Handles POST requests for updating the institution profile.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): The primary key of the institution profile.

        Returns:
            HttpResponseRedirect: Redirects to the institution profile list
            view.
        """
        profile = get_object_or_404(InstitutionProfile, pk=pk)
        serializer = InstitutionProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if not serializer.is_valid():
            return Response({"serializer": serializer, "profile": profile})

        serializer.save()

        return redirect("core-api:institution-profile-list")
