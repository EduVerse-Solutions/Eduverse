from django.urls import include, path

from core.api.utils import CustomDefaultRouter
from students.api import views as student_views

app_name = "students"

router = CustomDefaultRouter()

router.register(r"students", student_views.StudentViewSet, basename="student")
router.register(
    r"guardians", student_views.GuardianViewSet, basename="guardian"
)

urlpatterns = [
    path("", include(router.urls)),
]
