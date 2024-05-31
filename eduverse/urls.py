from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("", include("core.urls")),
    path("core-admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/swagger/", SpectacularSwaggerView.as_view(), name="swagger-docs"
    ),
    path("api/docs/", SpectacularRedocView.as_view(), name="api-docs"),
    path("api/", include("core.api.urls")),
    path("api/", include("students.api.urls")),
    path("api/", include("teachers.api.urls")),
    path("api/auth/", include("rest_framework.urls")),
    re_path(r"^oauth/", include("social_django.urls", namespace="social")),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns.append(path("debug/", include("debug_toolbar.urls")))

urlpatterns += staticfiles_urlpatterns()
