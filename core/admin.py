from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.forms import CoreUserAdminRegistrationForm
from core.models import Institution, User


class CoreUserAdmin(UserAdmin):
    """Custom User Administration Panel for EduVerse."""

    admin_site = admin.site
    admin_site.site_header = "EduVerse Admin"
    admin_site.site_title = "EduVerse Admin Portal"
    admin_site.index_title = "Welcome to EduVerse Admin Portal"

    add_form = CoreUserAdminRegistrationForm

    list_display = (
        "username",
        "role",
        "email",
        "phone_number",
        "institution",
    )
    search_fields = ["username", "phone_number"]
    list_filter = ["institution", "role"]

    form_fields = list(CoreUserAdminRegistrationForm.Meta.fields)

    # fields for user creation form
    add_fieldsets = (
        (
            None,
            {
                "classes": ["extrapretty"],
                "fields": CoreUserAdminRegistrationForm.Meta.fields,
            },
        ),
    )

    # fields for changing the user's details
    form_fields.remove("password1")
    form_fields.remove("password2")
    fieldsets = (
        (
            None,
            {
                "classes": ["extrapretty"],
                "fields": ["password"] + form_fields,
            },
        ),
    )


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "phone_number", "address")
    search_fields = ("name", "phone_number")
    list_filter = ["name"]


admin.site.register(User, CoreUserAdmin)
