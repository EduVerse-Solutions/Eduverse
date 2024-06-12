from django.urls import path

from core import views as core_views

app_name = "core"

urlpatterns = [
    path("", core_views.home, name="home"),
]
