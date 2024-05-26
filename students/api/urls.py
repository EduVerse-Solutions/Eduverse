from django.urls import include, path
from rest_framework import routers

from students.api import views as student_views

app_name = "students"

router = routers.DefaultRouter()
router.register(r"students", student_views.StudentViewSet, basename="student")
router.register(
    r"guardians", student_views.GuardianViewSet, basename="guardian"
)

urlpatterns = [
    path("", include(router.urls)),
]
