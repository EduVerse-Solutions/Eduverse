from django.urls import path

from core import views as core_views

app_name = "core"

urlpatterns = [
    path("", core_views.home, name="home"),
    path("institution/", core_views.institution, name="institution"),
    path(
        "update_institution/",
        core_views.add_institution,
        name="institution_update",
    ),
]
