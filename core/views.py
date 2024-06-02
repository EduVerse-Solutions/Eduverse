"""Views for the core app."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from core.forms import (
    InstitutionUpdateForm,
    UpdateProfileForm,
    UpdateUserForm,
    UserLoginForm,
    UserRegisterForm,
)


def home(request):
    return render(
        request, template_name="core/home.html", context={"name": "Home"}
    )


def institution(request):
    return render(request, "core/institution.html", {"name": "Institution"})


def add_institution(request):
    if request.method == "POST":
        form = InstitutionUpdateForm(
            request.POST, instance=request.user.institution
        )
        if form.is_valid():
            institution = form.save(commit=False)
            institution.owner = request.user
            institution.save()
            messages.success(request, "Institution updated successfully.")
            return redirect("core:institution")
    else:
        form = InstitutionUpdateForm(instance=request.user.institution)

    return render(
        request,
        "core/institution_change_form.html",
        {
            "form": form,
            "name": "Update Institution",
        },
    )


class UserRegisterView(View):
    """
    View for user registration.

    Attributes:
        form_class (Form): The form class for user registration.
        initial (dict): The initial data for the form.
        template_name (str): The template name for rendering the registration
        page.
    """

    form_class = UserRegisterForm
    initial = {}
    template_name = "core/register.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Return the user to the homepage if they are already authenticated and
        try to access register or related pages.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponseRedirect: The HTTP response redirecting to the homepage.

        """
        if request.user.is_authenticated:
            return redirect("core:home")

        return super(UserRegisterView, self).dispatch(
            request, *args, **kwargs
        )

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests for user registration.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The HTTP response object containing the rendered
            registration page.

        """
        form = self.form_class(initial=self.initial)
        return render(
            request, self.template_name, {"form": form, "name": "Register"}
        )

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests for user registration.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The HTTP response object containing the rendered
            registration page or redirecting to the login page.

        """
        form = self.form_class(request.POST, request=request)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get("username")
            messages.success(
                request,
                f"Account created for {username}. Log in to continue.",
            )

            return redirect("login")

        return render(
            request, self.template_name, {"form": form, "name": "Register"}
        )


class UserLoginView(LoginView):
    """
    View for user login.

    Attributes:
        form_class (Form): The form class for user login.
        extra_context (dict): Extra context data for rendering the login page.
    """

    form_class = UserLoginForm
    extra_context = {"name": "Login"}

    def form_valid(self, form):
        """
        Handles the validation of the login form.

        Args:
            form (Form): The login form.

        Returns:
            HttpResponse: The HTTP response object.

        """
        remember_me = form.cleaned_data.get("remember_me")

        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True

        return super(UserLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    """
    View for resetting user password.

    Attributes:
        template_name (str): The template name for rendering the password
        reset page.

        email_template_name (str): The template name for rendering the
        password reset email.

        subject_template_name (str): The template name for rendering the
        password reset email subject.

        success_message (str): The success message to be displayed after
        password reset.

        success_url (str): The URL to redirect to after successful password
        reset.

        extra_context (dict): Extra context data for rendering the password
        reset page.
    """

    template_name = "core/password_reset.html"
    email_template_name = "core/password_reset_email.html"
    subject_template_name = "core/password_reset_subject"
    success_message = (
        "If an account exists with the email you provided, you will receive "
        "instructions to set your password shortly. If not received, please "
        "verify the email address and check your spam folder."
    )
    success_url = reverse_lazy("core:home")
    extra_context = {"name": "Password Reset"}


@login_required
def profile(request):
    """
    View for user profile.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object containing the rendered profile
        page.
    """
    if request.method == "POST":
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile is updated successfully")
            return redirect(to="core:profile")
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(
        request,
        "users/profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "name": "Profile",
        },
    )


class ChangePasswordView(
    SuccessMessageMixin, PasswordChangeView, LoginRequiredMixin
):
    """
    View for changing user password.

    Attributes:
        template_name (str): The template name for rendering the change
        password page.
        success_message (str): The success message to be displayed after
        password change.
        success_url (str): The URL to redirect to after successful password
        change.
        extra_context (dict): Extra context data for rendering the change
        password page.
    """

    template_name = "users/change_password.html"
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy("users:home")
    extra_context = {"name": "Change Password"}


def auth_canceled(request):
    """
    Renders the 'auth_canceled.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered response containing the
        'auth_canceled.html' template.
    """
    return render(request, "users/auth_canceled.html")
