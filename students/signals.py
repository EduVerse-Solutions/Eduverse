from django.db.models.signals import post_save
from django.dispatch import receiver

from students.models import Guardian, Student


@receiver(signal=post_save, sender=Guardian)
def update_student_with_guardian_info(sender, instance, created, **kwargs):
    """
    Update the wards of a guardian with the guardian instance.

    Args:
        sender: The sender of the signal.
        instance: The instance of the Guardian model.
        created: A boolean indicating whether the instance was created or not.
        **kwargs: Additional keyword arguments.
    """
    if created or not created:
        for ward in instance.wards.all():
            ward.guardian = instance
            ward.save()


@receiver(signal=post_save, sender=Student)
def update_guardian_with_ward_info(sender, instance, created, **kwargs):
    """Update the guardian with the ward's information when it is added."""
    if instance.guardian is not None:
        instance.guardian.wards.add(instance.id)
