from uuid import uuid4

from django.db import models

from core.models import Institution, User


class Teacher(models.Model):
    """
    Represents a teacher in the system.

    Attributes:
        user (User): The user associated with the teacher.
        monthly_salary (Decimal): The monthly salary of the teacher.
    """

    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_salary = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )
    date_of_employment = models.DateField(null=False, blank=False)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.user.role = "Teacher"
        self.user.is_teacher = True
        self.user.save()
        super(Teacher, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.user.delete()
        super(Teacher, self).delete(*args, **kwargs)

    class Meta:
        ordering = ["user__last_name"]


class Class(models.Model):
    """
    Represents a class in the educational system.

    Attributes:
        teacher (Teacher): The teacher associated with the class.
        name (str): The name of the class.
        class_fee (Decimal): The fee for the class.
    """

    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, null=False, blank=False
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, null=False, blank=False
    )
    name = models.CharField(max_length=100, null=False, blank=False)
    class_fee = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, null=False
    )

    def __str__(self):
        return f"{self.name} - {self.institution}"

    class Meta:
        ordering = ["name"]
        unique_together = [
            "institution",
            "name",
        ]


class Subject(models.Model):
    """
    Represents a subject in the educational system.

    Attributes:
        class_name (ForeignKey): The class to which the subject belongs.
        name (CharField): The name of the subject.
        exam_mark (DecimalField): The maximum mark for the subject's exam.
    """

    id = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    class_id = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    exam_mark = models.DecimalField(max_digits=5, decimal_places=2)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        related_name="subjects_taught",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
