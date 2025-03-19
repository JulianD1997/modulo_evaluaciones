from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .forms import AssessmentForm, LoginForm
from .models import Assessment, Student, Teacher

# Función para crear datos de prueba
""" def create_data(request):
    fake = Faker()
    for i in range(20):
        student = Student.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            code=fake.unique.numerify("##########"),
            birth_date=fake.date_of_birth(minimum_age=17, maximum_age=50),
        )
        student.set_password("Admin1234+")
        student.save()
    for i in range(10):
        teacher = Teacher.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            dni=fake.unique.numerify("##########"),
        )
        teacher.save()
    return HttpResponse("Create data")
"""


# Función para iniciar sesión
def student_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        # Se valida el formulario
        if form.is_valid():
            code = form.cleaned_data["code"]
            password = form.cleaned_data["password"]
            # Se autentica el estudiante
            student = authenticate(request, code=code, password=password)
            # Si se pudo loguear se redirige a la página principal
            if student is not None:
                login(request, student)
                return redirect("Home")
            else:
                form.add_error(None, "Contraseña incorrecta")
    else:
        # se crea un formulario vacío
        form = LoginForm()
    # se renderiza la página de login
    return render(request, "layouts/login.html", {"form": form})


@login_required
def home_page(request):
    # Se obtiene el nombre del usuario logeado
    user_name = request.user.first_name + " " + request.user.last_name
    # re renderiza la página de inicio con el nombre del usuario
    return render(request, "layouts/home.html", {"user_name": user_name})


@login_required
def assessment_create(request):
    # obtiene el nombre del usuario logeado
    user_name = request.user.first_name + " " + request.user.last_name
    if request.method == "POST":
        form = AssessmentForm(
            request.POST
        )  # Se valida el formulario y se guarda la calificación
        if form.is_valid():
            student = request.user
            assessment = form.save(commit=False)
            assessment.student = student
            assessment.save()
            messages.success(
                request, f"Calificación Guardada para el Docente {assessment.teacher}"
            )
            # Crear un nuevo Formulario
            form = AssessmentForm(initial={"student": request.user})
            return redirect("Assessment")
    else:
        form = AssessmentForm(initial={"student": request.user})

    storage = messages.get_messages(request)
    storage.used = True
    return render(
        request, "layouts/assessment.html", {"form": form, "user_name": user_name}
    )


def find_assessment(request, id):
    students = list(Student.objects.values())
    return JsonResponse(students, safe=False)
