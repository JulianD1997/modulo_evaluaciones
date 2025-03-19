from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
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


# Función para iniciar sesión como estudiante
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
    return render(request, "layouts/login.html", {"form": form})


# Pagina principal por ahora muestra el nombre del estudiante logeado
@login_required
def home_page(request):
    user_name = request.user.first_name + " " + request.user.last_name
    return render(request, "layouts/home.html", {"user_name": user_name})


@login_required
def assessment_create(request):
    user_name = request.user.first_name + " " + request.user.last_name

    if request.method == "POST":
        form = AssessmentForm(request.POST)

        if form.is_valid():
            student = request.user
            assessment = form.save(commit=False)
            assessment.student = student
            assessment.save()
            messages.success(
                request, f"Calificación Guardada para el Docente {assessment.teacher}"
            )
            # Crear un nuevo Formulario con el estudiante logeado para que califique
            # a los docentes que hacen falta por evaluar
            form = AssessmentForm(initial={"student": request.user})
            return redirect("Assessment")
    else:
        form = AssessmentForm(initial={"student": request.user})

    # Se limpia la cola de mensajes
    storage = messages.get_messages(request)
    storage.used = True

    return render(
        request, "layouts/assessment.html", {"form": form, "user_name": user_name}
    )


@login_required
def view_assessments(request):
    user_name = request.user.first_name + " " + request.user.last_name
    # Datos que se van a enviar al template
    data = {"user_name": user_name}
    # Obtener todos los docentes
    query = request.GET.get("query", "").strip()
    if query:
        teachers = Teacher.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    else:
        teachers = Teacher.objects.all()

    teacher_data = []
    # Estudiantes totales
    students_count = Student.objects.count()
    for teacher in teachers:
        # Calculo promedio actual
        current_avg_data = Assessment.objects.filter(teacher=teacher).aggregate(
            rating_avg=Avg("rating"), total=Count("rating")
        )
        current_avg = current_avg_data["rating_avg"] or 1
        # Esta variable se puede usar para comparar los estudiantes que han realizado la evaluación
        total_ratings = current_avg_data["total"]
        # Calculo promedio total, aunque no hayan calificado se tiene en cuenta en este calculo
        total_avg = (current_avg / students_count) if students_count > 0 else 1
        # Datos para la lista de Docentes
        teacher_data.append(
            {
                "teacher": teacher,
                "current_avg": current_avg,
                "total_avg": total_avg,
            }
        )
    data["teacher_data"] = teacher_data
    return render(request, "layouts/view_assessment.html", data)


@login_required
def teacher_assessments(request, teacher_id):
    user_name = request.user.first_name + " " + request.user.last_name
    teacher = Teacher.objects.get(id=teacher_id)
    print(teacher)
    assessments = Assessment.objects.filter(teacher=teacher)
    data = {
        "user_name": user_name,
        "teacher": teacher,
        "assessments": assessments,
    }
    return render(request, "layouts/teacher_assessments.html", data)
