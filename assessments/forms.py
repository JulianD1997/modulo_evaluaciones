from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

from .models import Assessment, Student, Teacher


# Formulario para crear un nuevo estudiante
class StudentCreateForm(forms.ModelForm):
    # Campos para ingresar la contraseña y confirmarla
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg"}),
        required=True,
        label="Contraseña",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg"}),
        required=True,
        label="Confirmar Contraseña",
    )
    birth_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-lg", "type": "date"}
        ),
        label="Fecha de Nacimiento",
    )

    class Meta:
        # Para mostrar solo los campos que se requieren ingresar para crear el estudiante
        model = Student
        fields = [
            "first_name",
            "last_name",
            "email",
            "code",
            "birth_date",
            "password",
            "confirm_password",
        ]

    def __init__(self, *args, **kwargs):
        super(StudentCreateForm, self).__init__(*args, **kwargs)
        # Asignar la clase CSS 'form-control form-control-lg' a los campos de texto
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                field.widget.attrs.get("class", "") + " form-control form-control-lg"
            )

    def clean(self):
        # Validar que las contraseñas cumplan y coincidan
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Asegurarse de que ambos campos de contraseña están presentes
        if password and confirm_password:
            if password != confirm_password:
                self.add_error("confirm_password", "Las contraseñas no coinciden")

        return cleaned_data

    def save(self, commit=True):
        # Guardar el estudiante con la contraseña encriptada
        user = super().save(commit=False)
        user.set_password(
            self.cleaned_data["password"]
        )  # Usamos la contraseña validada
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
                r"^\d{1,10}$", "El código deber ser un numero de max 10 dígitos"
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
    rating = forms.IntegerField(
        label="Calificación",
        validators=[
            MinValueValidator(1, "No se permiten calificaciones menores a 1"),
            MaxValueValidator(5, "No se permiten calificaciones mayores a 5"),
        ],
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-control-lg",
            }
        ),
    )
    # Campo para Text Area para ingresar comentarios
    comment = forms.CharField(
        label="Comentarios",
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "Comentarios",
                "class": "form-control form-control-lg",
            }
        ),
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
