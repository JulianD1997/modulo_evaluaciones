from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

# Configuración de las rutas para la aplicación
urlpatterns = [
    # Ruta para la página principal
    path("", views.student_login, name="Login"),
    # Ruta para la página de inicio
    path("inicio/", views.home_page, name="Home"),
    # Ruta para evaluar
    path("evaluar/", views.assessment_create, name="Assessment"),
    # Ruta para cerrar sesión
    path("logout/", auth_views.LogoutView.as_view(), name="Logout"),
    
    path("find_assessments/<uuid:id>", views.find_assessment),
]
