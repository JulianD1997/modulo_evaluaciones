import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models


class Student(AbstractUser):
    # Se decide cambiar el id numerico por un UUID para evitar mejorar seguridad
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Se omiten campos innecesarios para el modelo estudiante
    username = None
    is_superuser = None
    is_staff = None

    # Se agrega el campo para ingresar el código del estudiante
    # Se valida que el código sea un número de máximo 10 dígitos
    code = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                r"^\d{1,10}$", "El código deber ser un numero de max 10 dígitos"
            )
        ],
    )
    # Se agrega el campo para la fecha del estudiante
    birth_date = models.DateField()

    # como se omite el username, se define el código como campo de autenticación
    USERNAME_FIELD = "code"
    # se define el campo email como requerido
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    # Se agrega el campo para ingresar la Cédula del profesor
    dni = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                r"^\d{8,10}$", "La cédula deber ser un numero de max 10 dígitos"
            )
        ],
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Assessment(models.Model):
    # Se valida el campo para que solo se pueda guardar un valor entre 1 y 5
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1, "No se permiten calificaciones menores a 1"),
            MaxValueValidator(5, "No se permiten calificaciones mayores a 5"),
        ],
    )
    comment = models.TextField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Se asegura que un estudiante solo pueda calificar una vez a un profesor
        constraints = [
            models.UniqueConstraint(
                fields=["student", "teacher"], name="unique_assessment"
            )
        ]

    def __str__(self):
        return f"{self.student} califico con {self.rating} a {self.teacher}"
