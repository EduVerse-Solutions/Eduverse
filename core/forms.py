"""
This module defines the forms. It includes forms for
user registration, login, and updating user information.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from core.models import Institution, User, Profile
from phonenumber_field.formfields import PhoneNumberField

FIELDS = [
    "first_name",
    "last_name",
    "fullname",
    "email",
    "username",
    "password1",
    "password2",
    "sex",
    "role",
    "date_of_birth",
    "institution",
    "phone_number",
    "address",
]


class CoreUserAdminRegistrationForm(UserCreationForm):
    """User creation form from the Administration platform."""

    username = forms.CharField()
    password1 = forms.CharField(
        label="Enter password", widget=forms.PasswordInput, required=True
    )
    password2 = forms.CharField(
        label="Confirm password", widget=forms.PasswordInput, required=True
    )

    class Meta:
        model = User
        fields = FIELDS

    def get_email(self):
        return self.cleaned_data.get("email")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")

        return password2

    def save(self, commit=True):
        user = super(CoreUserAdminRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class InstitutionUpdateForm(forms.ModelForm):
    """Form for changing the institution."""

    class Meta:
        model = Institution
        exclude = ["owner"]


class UserRegisterForm(UserCreationForm):
    """
    Form for user registration.

    Inherits from UserCreationForm provided by Django.
    Adds additional fields for first name, last name, email, date of birth,
    and institution name.
    """

    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "form-control mt-1 p-2 w-full bg-gray-100 rounded-md text-gray-900",
                "name": "first_name",
                "id": "first_name",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "form-control mt-1 p-2 w-full bg-gray-100 rounded-md text-gray-900",
                "name": "last_name",
                "id": "last_name",
            }
        ),
    )
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control mt-1 p-2 w-full bg-gray-100 rounded-md text-gray-900",
                "name": "username",
                "id": "username",
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control mt-1 p-2 w-full bg-gray-100 rounded-md text-gray-900",
                "name": "email",
            }
        ),
    )
    password1 = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control mt-1 p-2 w-full bg-gray-100 rounded-md text-gray-900",
                "data-toggle": "password",
                "id": "password1",
                "name": "password1",
            }
        ),
    )
    password2 = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "class": "form-control mt-1 p-2 w-full bg-gray-100 rounded-md text-gray-900",
                "data-toggle": "password",
                "id": "password2",
                "name": "password2",
            }
        ),
    )

    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                "placeholder": "Date of Birth",
                "class": "form-control mt-1 p-2 w-full bg-gray-100 rounded-md text-gray-900",
                "type": "date",
                "name": "date_of_birth",
                "id": "date_of_birth",
            }
        ),
    )

    institution_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Institution Name",
                "class": "form-control mt-1 p-2 w-full bg-gray-100 rounded-md text-gray-900",
                "name": "institution",
                "id": "institution_name",
            }
        ),
    )

    sex = forms.ChoiceField(
        choices=(('M', 'Male'), ('F', 'Female')),
        required=True,
        widget=forms.Select(
            attrs={'class': "form-control mt-1 p-2 w-full bg-gray-100 rounded-md text-gray-900", 'readonly': False, 'id': 'sex'}
        )
    )

    phone_number = PhoneNumberField(
    widget=forms.TextInput(
        attrs={
            "placeholder": "Phone Number",
            "class": "form-control mt-1 p-2 w-full bg-gray-100 rounded-md text-gray-900",
            "name": "phone_number",
            "id": "phone_number",
        }
    ),
    required=True,
)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "date_of_birth",
            "institution_name",
            "password1",
            "password2",
            "phone_number",
            "sex",
        ]

    def save(self, commit=True):
        """
        Save the user registration form.

        Overrides the save method of UserCreationForm.
        Creates a new user object and saves it to the database.
        Creates a new institution object and assigns it to the user's
        institution field.
        """

        # Call the original save method to get a user object
        user = super().save(commit=False)

        # Save the user object if commit is True
        if commit:
            user.save()

        # Create a new institution object from the institution_name field
        institution, created = Institution.objects.get_or_create(
            name=self.cleaned_data["institution_name"], owner=user
        )

        # Assign the institution object to the user's institution field
        user.institution = institution
        institution.save()

        return user


class UserLoginForm(AuthenticationForm):
    """
    Form for user login.

    Inherits from AuthenticationForm provided by Django.
    Adds additional field for email and customizes the form behavior.
    """

    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control mt-1 p-2 w-full bg-gray-100 rounded-md text-gray-900",
                "name": "email",
                "id": "email",
            }
        ),
    )
    password = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control mt-1 p-2 w-full bg-gray-100 rounded-md text-gray-900",
                "data-toggle": "password",
                "id": "password",
                "name": "password",
            }
        ),
    )
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ["email", "password", "remember_me"]

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields["username"].required = False
        self.fields["email"].required = True

    def clean(self):
        """
        Clean and validate the form data.

        Overrides the clean method of AuthenticationForm.
        Authenticates the user based on the provided email and password.
        """

        username = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if username and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                    params={"username": self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UpdateUserForm(forms.ModelForm):
    """
    Form for updating user information.

    Inherits from ModelForm provided by Django.
    Provides fields for updating username and email.
    """

    class Meta:
        model = User
        fields = ["username", "email"]


class UpdateProfileForm(forms.ModelForm):
    """
    Form for updating user profile information.

    Inherits from ModelForm provided by Django.
    Provides fields for updating avatar and bio.
    """

    class Meta:
        model = Profile
        fields = ["avatar", "bio"]
