from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

from .models import Assessment, Student, Teacher


class StudentCreateForm(forms.ModelForm):
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
        model = Student
        fields = ["first_name", "last_name", "email", "code", "birth_date"]

    def clean_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
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
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg"}),
        required=True,
    )


class AssessmentForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        label="Docente",
        widget=forms.Select(attrs={"class": "form-control form-control-lg"}),
    )
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
        model = Assessment
        fields = ["teacher", "rating", "comment"]

    def clean_teacher(self):
        teacher = self.cleaned_data.get("teacher")
        if not teacher:
            raise forms.ValidationError("Seleccione un docente")
        return teacher
