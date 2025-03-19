from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from faker import Faker

from .forms import LoginForm
from .models import Assessment, Student, Teacher

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


def student_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            password = form.cleaned_data["password"]
            student = authenticate(request, code=code, password=password)
            if student is not None:
                login(request, student)
                return HttpResponse("Login correcto")
            else:
                form.add_error(None, "Contraseña incorrecta")
    else:
        form = LoginForm()

    return render(request, "layouts/login.html", {"form": form})


def find_assessment(request, id):
    students = list(Student.objects.values())
    return JsonResponse(students, safe=False)
