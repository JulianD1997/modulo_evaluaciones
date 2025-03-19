from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

from .models import Assessment, Student, Teacher


# Formulario para crear un nuevo estudiante
class StudentCreateForm(forms.ModelForm):
    # Campos para ingresar la contraseña y confirmarla
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,
        label="Contraseña",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,
        label="Confirmar Contraseña",
    )

    class Meta:
        # Para mostrar solo los campos que se requieren ingresar para crear el estudiante
        model = Student
        fields = ["first_name", "last_name", "email", "code", "birth_date"]

    def clean_password(self):
        # Validar que las contraseñas cumplan y coincidan
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password

    def save(self, commit=True):
        # Guardar el estudiante con la contraseña encriptada
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# Formulario para iniciar sesión
class LoginForm(forms.Form):
    # Campo para ingresar el código del estudiante
    code = forms.CharField(
        label="Código Estudiante",
        max_length=10,
        validators=[
            RegexValidator(
                r"^\d{10}$", "El código debe ser un número de máximo 10 dígitos"
            )
        ],
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg"}),
    )
    # Campo para ingresar la contraseña
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg"}),
        required=True,
    )


# Formulario para evaluar a un docente
class AssessmentForm(forms.ModelForm):
    # Traer todos los docentes para seleccionar uno
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        label="Docente",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    # Campo para ingresar un numero decimal
    rating = forms.DecimalField(
        label="Calificación",
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(1.0, "No se permiten calificaciones menores a 1.0"),
            MaxValueValidator(5.0, "No se permiten calificaciones mayores a 5.0"),
        ],
        widget=forms.NumberInput(attrs={"class": "form-control form-control-lg"}),
    )
    # Campo para Text Area para ingresar comentarios
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "Comentarios",
                "class": "form-control form-control-lg",
            }
        )
    )

    class Meta:
        # Como se espera que el estudiante este logeado no es necesario ingresar el campo student
        model = Assessment
        fields = ["teacher", "rating", "comment"]

    def __init__(self, *args, **kwargs):
        # Para evitar que el estudiante escoja un docente que ya haya sido evaluado
        # Se filtran los docentes que ya han sido evaluados
        if "initial" in kwargs:
            student = kwargs["initial"]["student"]
        else:
            student = None
        super(AssessmentForm, self).__init__(*args, **kwargs)
        print(student)
        if student:
            print("entro")
            excluded_teacher = Assessment.objects.filter(student=student).values_list(
                "teacher", flat=True
            )
            self.fields["teacher"].queryset = Teacher.objects.exclude(
                id__in=excluded_teacher
            )

    def clean_teacher(self):
        # Validar que se seleccione un docente
        teacher = self.cleaned_data.get("teacher")
        if not teacher:
            raise forms.ValidationError("Seleccione un docente")
        return teacher
