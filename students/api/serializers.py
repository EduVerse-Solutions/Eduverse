from rest_framework import serializers, status
from rest_framework.response import Response

from core.api.serializers import UserSerializer
from core.models import User
from students.models import Guardian, Student


class BaseUserModelSerializer(serializers.ModelSerializer):
    """
    Serializer for the BaseUserModel class.
    """

    user = UserSerializer(required=False)

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
        wards_data = validated_data.pop("wards", [])
        user_data = validated_data.pop("user", None)

        if user_data:
            print("over here")
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        if wards_data:
            # there are new wards for a Guardian
            ward_ids = [ward.id for ward in wards_data]
            wards = Student.objects.filter(id__in=ward_ids)

            instance.wards.set(wards)

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
            for ward in instance.wards:
                ward.delete()

        instance.delete()


class StudentSerializer(BaseUserModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="students:student-detail"
    )

    class Meta(BaseUserModelSerializer.Meta):
        model = Student
        # depth = 1

    # guardian = serializers.HyperlinkedRelatedField(
    #     view_name="students:guardian-detail",
    #     queryset=Guardian.objects.all(),
    #     required=False,
    # )


class GuardianSerializer(BaseUserModelSerializer):
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
        wards = validated_data.pop("wards", [])
        ward_ids = [ward.id for ward in wards]
        user_data = validated_data.pop("user")
        user, created = User.objects.get_or_create(
            email=user_data.get("email"), defaults=user_data
        )
        if created:
            guardian = Guardian.objects.create(user=user)
            wards = Student.objects.filter(id__in=ward_ids)
            guardian.wards.set(ward_ids)
            return guardian
        else:
            raise serializers.ValidationError(
                "A user with this email already exists..."
            )

    def validate(self, data):
        """
        Validates that the wards are Student instances.

        This method is called during the validation process of the serializer.
        It checks if all the wards provided are instances of the Student model.
        If any ward is not an instance of the Student model, a validation error
        is raised.

        Args:
            data (dict): The data to be validated.

        Raises:
            serializers.ValidationError: If any ward is not an instance of the
                Student model.

        Returns:
            dict: The validated data.
        """
        wards = data.get("wards")

        if not all(isinstance(ward, Student) for ward in wards):
            raise serializers.ValidationError(
                {"wards": "All wards must be Student instances"},
                code="invalid",
            )

        return data
