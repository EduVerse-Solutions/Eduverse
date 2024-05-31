from django.urls import include, path

from core.api.utils import CustomDefaultRouter
from teachers.api import views as teacher_views

app_name = "teachers"

router = CustomDefaultRouter()
router.register(r"teachers", teacher_views.TeacherViewSet, basename="teacher")
router.register(r"classes", teacher_views.ClassViewSet, basename="class")
router.register(r"subjects", teacher_views.SubjectViewSet, basename="subject")

urlpatterns = [
    path("", include(router.urls)),
]
