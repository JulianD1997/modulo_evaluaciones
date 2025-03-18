import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models


class Student(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    is_superuser = None
    is_staff = None

    code = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                r"^\d{10}$", "El código deber ser un numero de max 10 dígitos"
            )
        ],
    )
    birth_date = models.DateField()

    USERNAME_FIELD = "code"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} code: {self.code}"


class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dni = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                r"^\d{10}$", "La cédula deber ser un numero de max 10 dígitos"
            )
        ],
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} dni: {self.dni}"


class Assessment(models.Model):
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(1.0, "No se permiten calificaciones menores a 1.0"),
            MaxValueValidator(5.0, "No se permiten calificaciones mayores a 5.0"),
        ],
    )
    comment = models.TextField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["teacher", "student"]

    def __str__(self):
        return f"{self.student} califico con {self.rating} a {self.teacher}"
