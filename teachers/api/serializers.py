from rest_framework import serializers

from students.api.serializers import BaseUserModelSerializer
from teachers.models import Class, Subject, Teacher


class TeacherSerializer(BaseUserModelSerializer):
    """Teacher serializer."""

    url = serializers.HyperlinkedIdentityField(
        view_name="teachers:teacher-detail"
    )

    subjects_taught = serializers.SerializerMethodField()

    def get_subjects_taught(self, obj):
        subjects = obj.subjects_taught.all()
        return SubjectSerializer(
            subjects,
            many=True,
            context={"request": self.context.get("request")},
        ).data

    class Meta(BaseUserModelSerializer.Meta):
        model = Teacher


class ClassSerializer(serializers.ModelSerializer):
    """Class serializer."""

    url = serializers.HyperlinkedIdentityField(
        view_name="teachers:class-detail"
    )

    class Meta(BaseUserModelSerializer.Meta):
        model = Class


class SubjectSerializer(serializers.ModelSerializer):
    """Subject serializer."""

    url = serializers.HyperlinkedIdentityField(
        view_name="teachers:subject-detail"
    )

    class Meta(BaseUserModelSerializer.Meta):
        model = Subject
