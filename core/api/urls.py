from django.contrib.auth import views as auth_views
from django.urls import include, path

from core.api import views as core_api_views
from core.api.utils import CustomDefaultRouter

app_name = "core-api"

router = CustomDefaultRouter()
router.register(r"users", core_api_views.UserViewSet, basename="user")
router.register(
    r"institutions", core_api_views.InstitutionViewSet, basename="institution"
)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "auth/login/",
        auth_views.LoginView.as_view(
            template_name="api/login.html",
        ),
        name="login",
    ),
]
