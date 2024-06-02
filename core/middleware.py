from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from social_core.exceptions import AuthCanceled

from core.models import User


class AdminAccessMiddleware:
    """
    Middleware class to restrict access to admin pages.

    This middleware checks if the user is authenticated and has staff privileges
    before allowing access to admin pages. If the user is not authenticated or
    does not have staff privileges, they are redirected to the home page with an
    error message.

    Attributes:
        get_response (function): The next middleware or view function in the
        chain.

    Methods:
        __call__(self, request): Checks if the user is allowed to access the
        admin page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Checks if the user is allowed to access the admin page.

        Args:
            request (HttpRequest): The incoming request object.

        Returns:
            HttpResponse: The response object.

        """
        if request.path.startswith(reverse("admin:index")):
            if not (request.user.is_authenticated and request.user.is_staff):
                messages.error(
                    request, "You are not allowed to access this page."
                )
                return HttpResponseRedirect(reverse("core:home"))
        return self.get_response(request)


class InstitutionCheckMiddleware(MiddlewareMixin):
    """
    Middleware class to check if the authenticated user has created an
    organization.

    If the user is authenticated and has the role of "Super Admin", this
    middleware checks if the user has created an organization. If not, it
    displays a message prompting the user to create an organization in the
    profile section.
    """

    def process_request(self, request):
        user: User = request.user
        if user.is_authenticated and user.role == "Super Admin":
            if user.is_superuser:
                return  # don't show the message to the site admin
            if user.institution is None:
                messages.warning(
                    request,
                    message="You have not created an organization yet. Please "
                    "do that in the institution section",
                )


class SocialAuthExceptionMiddleware:
    """
    Middleware class to handle social authentication exceptions.

    This middleware class is responsible for catching exceptions related to
    social authentication and redirecting the user to the appropriate page
    based on the exception type.

    Attributes:
        get_response (function): The callable that represents the next
        middleware or view in the chain.

    Methods:
        __call__(self, request): Process the request and return the response.
        process_exception(self, request, exception): Handle the exception and
        return the appropriate response.
    """

    def __init__(self, get_response):
        """
        Initializes a new instance of the Middleware class.

        Args:
            get_response (function): The function to be called to get the
            response.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the request and return the response.

        Args:
            request (HttpRequest): The incoming request object.

        Returns:
            HttpResponse: The response object.
        """
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Handle the exception and return the appropriate response.

        Args:
            request (HttpRequest): The incoming request object.
            exception (Exception): The exception object.

        Returns:
            HttpResponseRedirect: The response object for redirecting the user.

        """
        if isinstance(exception, AuthCanceled):
            return HttpResponseRedirect(reverse("auth_canceled"))
