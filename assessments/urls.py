from django.urls import path
from . import views

urlpatterns = [
    path("", views.student_login, name="Login"),
    path("find_assessments/<uuid:id>", views.find_assessment),
]
