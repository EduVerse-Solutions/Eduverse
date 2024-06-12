from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from core.models import Institution, InstitutionProfile, User, UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Signal receiver function to create an authentication token for a newly
    created user.

    Args:
        sender: The model class that sent the signal.
        instance: The actual instance being saved.
        created: A boolean value indicating whether the instance was created
        or updated.
        **kwargs: Additional keyword arguments.:
    """
    user = User.objects.get(id=instance.id)
    if created and user.role in ["Super Admin", "Admin"]:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Institution)
def assign_institution_owner(sender, instance, created, **kwargs):
    """
    Assigns the institution owner to the instance and saves the changes.

    Args:
        sender: The sender of the signal.
        instance: The instance of the Institution model being saved.
        created: A boolean indicating whether the instance was created or not.
        **kwargs: Additional keyword arguments.
    """
    if created:
        user = User.objects.get(id=instance.owner_id)
        user.institution = instance
        instance.owner = user
        instance.save()
        user.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance: User, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Institution)
def save_institution_profile(sender, instance: Institution, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()
    else:
        InstitutionProfile.objects.create(institution=instance)
