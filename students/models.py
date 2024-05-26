from django.db import models

from core.models import User
from core.validators import Validators


class Student(models.Model):
    """Student model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admission_number = models.CharField(max_length=20, unique=True)
    date_of_admission = models.DateField(null=False, blank=False)
    date_of_graduation = models.DateField(null=True, blank=True)
    guardian = models.ForeignKey(
        "Guardian",
        on_delete=models.CASCADE,
        related_name="guardian",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.user.fullname} - {self.admission_number}"

    def save(self, *args, **kwargs) -> None:
        self.user.role = "Student"  # enforce the role
        Validators.run_validators(user=self.user)
        Validators.validate_user_belongs_to_institution(
            user=self.user, institution=self.user.institution
        )
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["id"]


class Guardian(models.Model):
    """Guardian model."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="guardian",
        null=False,
    )
    wards = models.ManyToManyField("Student", related_name="guardians")

    def __str__(self) -> str:
        admission_numbers = ", ".join(
            ward.admission_number for ward in self.wards.all()
        )
        return f"{self.user.fullname} - {admission_numbers}"

    def save(self, *args, **kwargs) -> None:
        """Save the Guardian."""
        self.user.role = "Guardian"
        Validators.run_validators(user=self.user)
        Validators.validate_user_belongs_to_institution(
            user=self.user, institution=self.user.institution
        )
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete all the students when a guardian is deleted."""
        self.wards.all().delete()
        self.delete()
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ["id"]
