from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Student, Teacher
from faker import Faker


class TestModels(TestCase):
    def setUp(self):
        fake = Faker()

        for i in range(20):
            student = Student.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                code=fake.unique.numerify("##########"),
                birth_date=fake.date_of_birth(minimum_age=17, maximum_age=50),
                password="Admin1234+",
            )
            student.save()
        for i in range(10):
            teacher = Teacher.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                dni=fake.unique.numerify("##########"),
            )
            teacher.save()

    def test_create_student_teacher(self):
        teachers = Teacher.objects.all()
        self.assertEqual(teachers.count(), 10)

        students = Student.objects.all()
        self.assertEqual(students.count(), 20)

        student = students[0]
        self.assertTrue(student.first_name)
        self.assertTrue(student.code)

        teacher = teachers[0]
        self.assertTrue(teacher.first_name)
        self.assertTrue(teacher.dni)
