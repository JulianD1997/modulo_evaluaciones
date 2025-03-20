from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AssessmentForm, LoginForm, StudentCreateForm
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
                form.fields["password"].error_messages = {
                    "invalid": "Contraseña incorrecta"
                }
                form.add_error("password", "Código o Contraseña incorrecta")
                print(form.errors)
    else:
        # se crea un formulario vacío
        form = LoginForm()
    return render(request, "layouts/login_page.html", {"form": form})


def student_register(request):
    if request.method == "POST":
        form = StudentCreateForm(request.POST)
        # Se valida el formulario
        if form.is_valid():
            # Guardar al estudiante con la contraseña encriptada
            form.save()
            # Mostrar mensaje de éxito
            messages.success(request, "¡Registro exitoso! Ahora puedes iniciar sesión.")
            # Redirigir al usuario a la página de login
            return redirect("Login")
        else:
            # Si el formulario no es válido, mostrar mensaje de error
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        # Si es un GET, creamos un formulario vacío
        form = StudentCreateForm()

    return render(request, "layouts/register_page.html", {"form": form})


# Pagina principal por ahora muestra el nombre del estudiante logeado
@login_required
def home_page(request):
    user_name = request.user.first_name + " " + request.user.last_name
    return render(request, "layouts/home_page.html", {"user_name": user_name})


@login_required
def assessment_create(request):
    user_name = request.user.first_name + " " + request.user.last_name

    if request.method == "POST":
        form = AssessmentForm(request.POST)
        if form.is_valid():
            student = request.user
            try:
                assessment = form.save(commit=False)
                assessment.student = student
                assessment.save()
                # Mostrar mensaje para confirmar que se guardo la calificación
                messages.success(
                    request,
                    f"Calificación guardada para el Docente {assessment.teacher}",
                )
                # Se crea un nuevo formulario para que el estudiante pueda calificar a otro docente
                form = AssessmentForm(initial={"student": request.user})
                return redirect("Assessment")
            except Exception as e:
                # en caso suceda algún error
                messages.error(
                    request, f"Hubo un error al guardar la evaluación: {str(e)}"
                )
        else:
            # si hay errores en el formulario
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = AssessmentForm(initial={"student": request.user})

    return render(
        request, "layouts/assessment_page.html", {"form": form, "user_name": user_name}
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
            Q(first_name__istartswith=query) | Q(last_name__istartswith=query)
        )
    else:
        teachers = Teacher.objects.all().prefetch_related("assessment_set")

    if not teachers:
        messages.warning(request, "No se encontraron docentes")
        return render(request, "layouts/view_assessment.html", data)

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
        sum_missing_ratings = students_count - total_ratings

        """ Calculo promedio total, aunque no hayan calificado se tiene en cuenta 
        en este calculo las calificaciones que no se han hecho se tienen en cuenta 
        como la calificación mas baja posible """
        total_avg = round(
            (
                ((current_avg + sum_missing_ratings) / students_count)
                if students_count > 0
                else 1
            ),
            1,
        )
        # Datos para la lista de Docentes
        teacher_data.append(
            {
                "teacher": teacher,
                "current_avg": current_avg,
                "total_avg": total_avg,
            }
        )
    data["teacher_data"] = teacher_data
    return render(request, "layouts/view_assessment_page.html", data)


@login_required
def teacher_assessments(request, teacher_id):
    user_name = request.user.first_name + " " + request.user.last_name
    # En dado caso el ID no exista se envía un error 404
    teacher = get_object_or_404(Teacher, id=teacher_id)
    print(teacher)
    assessments = Assessment.objects.filter(teacher=teacher)
    data = {
        "user_name": user_name,
        "teacher": teacher,
        "assessments": assessments,
    }
    return render(request, "layouts/teacher_assessments_page.html", data)
