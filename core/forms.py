from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from core.models import Institution, User

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
