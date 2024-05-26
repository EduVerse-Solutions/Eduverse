from rest_framework import status
from rest_framework.response import Response

from core.api.serializers import UserSerializer


class UserUpdateMixin:
    """
    A mixin class for updating user data.

    This mixin provides a method for updating user data in a view set.
    """

    def update(self, request, *args, **kwargs):
        """
        Update user data.

        This method updates the user data based on the request data.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object containing the updated user data.
        """
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            user = instance.user

            if "user" in request.data:
                user_data = request.data.pop("user")
                user_serializer = UserSerializer(
                    user,
                    data=user_data,
                    partial=True,
                    context={"request": request, "user": user},
                )
                user_serializer.is_valid(raise_exception=True)

                user_serializer.save()

            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, "_prefetched_objects_cache", None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)

        except Exception as e:
            if "detail" in vars(e):
                return Response(
                    {"error": {k: v for k, v in e.detail.items()}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(str(e), status=status.HTTP_417_EXPECTATION_FAILED)


class UserDestroyMixin:
    """
    Mixin class for destroying a user instance along with its associated object.

    This mixin provides a `destroy` method that deletes the user instance and
    its associated object.

    Attributes:
        None

    Methods:
        destroy(request, *args, **kwargs): Deletes the user instance and its
        associated object.
    """

    def destroy(self, request, *args, **kwargs):
        """
        Deletes the user instance and its associated object.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response with status code 204 (No Content).

        """
        instance = self.get_object()
        if instance.wards:
            for ward in instance.wards:
                ward.delete()
        user = instance.user
        self.perform_destroy(instance)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
