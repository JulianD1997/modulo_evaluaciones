from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

# Configuración de las rutas para la aplicación
urlpatterns = [
    # Ruta para la página de inicio
    path("", views.home_page, name="Home"),
    # Ruta para la página principal
    path("login/", views.student_login, name="Login"),
    # Ruta para evaluar
    path("docente/evaluar/", views.assessment_create, name="Assessment"),
    # Ruta para visualizar las calificaciones de los docentes
    path("docentes/listado/", views.view_assessments, name="View_assessments"),
    # Ruta para ver las calificaciones de un docente
    path(
        "docentes/<int:teacher_id>/evaluaciones/",
        views.teacher_assessments,
        name="Teacher_assessments",
    ),
    # Ruta para cerrar sesión
    path("logout/", auth_views.LogoutView.as_view(), name="Logout"),
    # path("find_assessments/<uuid:id>", views.find_assessment),
]
