from random import choice

from django.urls import reverse
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.routers import APIRootView, DefaultRouter

from core.api import data
from core.api.permissions import IsSuperAdminOrAdmin
from core.models import Institution, User


class PaginationWithLinks(PageNumberPagination):
    """
    A custom pagination class that includes links to the next and previous
    pages.

    Attributes:
        page_size (int): The number of items to include on each page.
        page_size_query_param (str): The query parameter to control the page
        size.
        max_page_size (int): The maximum allowed page size.
        page_query_param (str): The query parameter to control the current
        page number.
        last_page_strings (tuple): A tuple of strings to represent the last
        page in the pagination response.
    """

    def get_paginated_response(self, data) -> Response:
        """
        Get the paginated response with links to the next and previous pages.

        Args:
            data (list): The paginated data.

        Returns:
            dict: The paginated response containing links, count, total pages,
            current page, and results.
        """
        return Response(
            data={
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "status_code": Response.status_code,
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "data": data,
            }
        )


class EduverseAPIRoot(APIRootView):
    """
    A view which returns a list of all existing endpoints, not just the ones on this router.
    """

    permission_classes = [IsSuperAdminOrAdmin]

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        base_names = [
            "students:student-list",
            "students:guardian-list",
            "teachers:teacher-list",
            "teachers:class-list",
            "teachers:subject-list",
        ]
        for basename in base_names:
            relative_url = reverse(basename)
            absolute_url = request.build_absolute_uri(relative_url)
            key = absolute_url.split("/")[-2]
            response.data[key] = absolute_url
        return response


class CustomDefaultRouter(DefaultRouter):
    APIRootView = EduverseAPIRoot

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = "/?"


def create_super_admin(assign_institution=False, **kwargs):
    """
    Creates a user from super admin user using the data in the user_list.
    """
    if kwargs:
        user_data = kwargs
    else:
        user_data = data.user_list[0]

    if assign_institution:
        user = User.objects.create(**user_data)
        institution = Institution.objects.create(
            # trunk-ignore(bandit/B311)
            **choice(data.institution_list),
            owner=user,
        )
        user.institution = institution
        return user

    return User.objects.create(**user_data)


def create_student(assign_institution=False):
    """
    Creates a student user using the data in the user_list.
    """
    if assign_institution:
        super_admin = create_super_admin(assign_institution=True)

        user = User.objects.create(**data.user_list[1])
        user.institution = super_admin.institution
        return user

    return User.objects.create(**data.user_list[1])


def create_guardian(assign_institution=False):
    """
    Creates a guardian user using the data in the user_list.
    """
    if assign_institution:
        super_admin = create_super_admin(assign_institution=True)

        user = User.objects.create(**data.user_list[2])
        user.institution = super_admin.institution
        return user

    return User.objects.create(**data.user_list[2])
