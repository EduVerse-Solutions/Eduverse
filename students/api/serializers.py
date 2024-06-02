from rest_framework import serializers, status
from rest_framework.response import Response

from core.api.serializers import UserSerializer
from core.models import User
from students.api.validators import (
    GuardianValidationMixin,
    StudentValidationMixin,
)
from students.models import Guardian, Student


class BaseUserModelSerializer(serializers.ModelSerializer):
    """
    Serializer for the BaseUserModel class.
    """

    user = UserSerializer()

    class Meta:
        fields = "__all__"
        read_only_fields = ["id"]

    def create(self, validated_data):
        """
        Create a new instance of the model with the given validated data.

        Args:
            validated_data (dict): The validated data for creating the instance.

        Returns:
            The created instance.

        Raises:
            Exception: If there is an error during the creation process.
        """
        user_data = validated_data.pop("user")
        user_data["role"] = self.Meta.model.__name__

        user = User.objects.create(**user_data)
        try:
            return self.Meta.model.objects.create(user=user, **validated_data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, instance, validated_data, partial=False):
        """
        Update an existing instance of the model with the given validated data.

        Args:
            instance: The instance to be updated.
            validated_data (dict): The validated data for updating the instance.
            partial (bool, optional): Whether to perform a partial update or
            not. Defaults to True.

        Returns:
            The updated instance.
        """
        user_data = validated_data.pop("user", None)

        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        elif partial:
            for attr, value in validated_data.items():
                if hasattr(instance, attr):
                    setattr(instance, attr, value)
        else:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

        instance.save()
        return instance

    def delete(self, instance):
        """
        Delete an instance of the model.

        Args:
            instance: The instance to be deleted.
        """
        user = instance.user
        user.delete()
        if instance.wards:
            # disassociate wards from guardian
            instance.wards.clear()

        instance.delete()


class StudentSerializer(StudentValidationMixin, BaseUserModelSerializer):
    """
    Serializer class for the Student model.

    This serializer is used to convert the Student model instances into JSON
    representations and vice versa. It also includes validation logic for the
    student data.

    Attributes:
        url: A hyperlink identity field that represents the URL of the student
        detail view.

    Meta:
        model: The Student model that this serializer is associated with.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="students:student-detail"
    )

    class Meta(BaseUserModelSerializer.Meta):
        model = Student

    # let's create an update method that also looks out for the guardian field
    # and sets it on the student
    def update(self, instance, validated_data, partial=False):
        """
        Update an existing instance of the model with the given validated data.

        Args:
            instance: The instance to be updated.
            validated_data (dict): The validated data for updating the instance.
            partial (bool, optional): Whether to perform a partial update or
            not. Defaults to True.

        Returns:
            The updated instance.
        """
        guardian = validated_data.pop("guardian", None)
        print(validated_data)

        if guardian:
            instance.guardian = guardian
            instance.save()

        return super().update(instance, validated_data, partial)


class GuardianSerializer(GuardianValidationMixin, BaseUserModelSerializer):
    """
    Serializer for the Guardian model.

    This serializer is used to convert Guardian model instances into JSON
    representations and vice versa. It provides validation for the wards field
    to ensure that all wards are instances of the Student model.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="students:guardian-detail"
    )

    class Meta(BaseUserModelSerializer.Meta):
        model = Guardian

    wards = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Student.objects.all()
    )

    def create(self, validated_data):
        """
        Create a new guardian instance with the provided validated data.

        Args:
            validated_data (dict): The validated data for creating the guardian.

        Returns:
            Guardian: The created guardian instance.
        """
        wards = validated_data.pop("wards", [])
        ward_ids = [ward.id for ward in wards]
        user_data = validated_data.pop("user")
        user_data["role"] = self.Meta.model.__name__
        user, created = User.objects.get_or_create(
            email=user_data.get("email"), defaults=user_data
        )
        if created:
            guardian = Guardian.objects.create(user=user)
            wards = Student.objects.filter(id__in=ward_ids)
            guardian.wards.set(ward_ids)

            # for each ward, set their guardian field to this guardian
            for ward in wards:
                ward.guardian = guardian
                ward.save()

            return guardian
