from django.urls import path

from . import views

urlpatterns = [
    path("", views.student_login, name="Login"),
    path("inicio/", views.home_page, name="Home"),
    path("evaluar/", views.assessment_create, name="Assessment"),
    path("find_assessments/<uuid:id>", views.find_assessment),
]
