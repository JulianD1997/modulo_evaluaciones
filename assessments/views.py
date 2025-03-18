from django.http import HttpResponse
from django.shortcuts import render
from faker import Faker

from .models import Student, Teacher



def create_data(request):
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
