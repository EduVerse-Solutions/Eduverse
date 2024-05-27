from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from core.api.serializers import UserSerializer
from students.models import Guardian


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
            else:
                user_data = vars(user)

            user_data.pop("url", None)
            user_serializer = UserSerializer(
                user,
                data=user_data,
                partial=True,
                context={"request": request, "user": user},
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

            if partial:
                request.data["user"] = user_data

            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, "_prefetched_objects_cache", None):
                # If 'prefetch_related' has been applied to a queryset, we
                # need to forcibly invalidate the prefetch cache on the
                # instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)

        except Exception as error:
            # check for django unique key constraints, these are not actual
            # errors per project, we will ignore this one and get the results
            # we asked for
            if isinstance(error, IntegrityError) or "already exists" in str(
                error
            ):
                view = request.parser_context.get("view")
                user.__dict__.update(user_data)
                user.save()
                guardian_id = request.data.get("guardian")

                if guardian_id:
                    instance.guardian = get_object_or_404(
                        Guardian, id=guardian_id
                    )
                else:
                    try:
                        guardian = Guardian.objects.get(wards=instance)
                        guardian.wards.remove(instance)
                    except Guardian.DoesNotExist:
                        pass

                    # Set the guardian of the instance to None
                    instance.guardian = None

                # Update the instance with the rest of the data
                instance.__dict__.update(request.data)
                instance.save()
                response = view.get(request)
                return Response(response.data)

            elif "detail" in vars(error) and isinstance(error.detail, dict):
                return Response(
                    {"error": {k: v for k, v in error.detail.items()}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "error": {
                        str(error.__class__.__name__): [
                            error.args,
                            error.__traceback__.tb_frame.f_globals[
                                "__file__"
                            ],
                        ]
                    }
                },
                status=status.HTTP_417_EXPECTATION_FAILED,
            )


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
            instance.wards.all().delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
