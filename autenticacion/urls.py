"""
URLs para la aplicación de autenticación - Sistema completo Roy Representaciones
"""
from django.urls import path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from autenticacion.views import SidebarView

app_name = 'autenticacion'

urlpatterns = [
    # Páginas web de autenticación
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('registro/', TemplateView.as_view(template_name='registro.html'), name='registro'),
    path('logout/', views.logout_view, name='logout'),
    
    # APIs REST para autenticación con JWT
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/registro/', views.RegistroAPIView.as_view(), name='api_registro'),
    path('api/perfil/', views.PerfilAPIView.as_view(), name='api_perfil'),
    path('api/cambiar-password/', views.CambiarPasswordAPIView.as_view(), name='api_cambiar_password'),
    
    # APIs de validación
    path('api/validar-usuario/', views.ValidarUsuarioAPIView.as_view(), name='api_validar_usuario'),
    path('api/validar-cedula/', views.ValidarCedulaAPIView.as_view(), name='api_validar_cedula'),
    path('api/validar-correo/', views.ValidarCorreoAPIView.as_view(), name='api_validar_correo'),
    
    # JWT token refresh
    path('api/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('api/verificar-token/', views.VerificarTokenAPIView.as_view(), name='api_verificar_token'),
    
    # Utilidades
    path('api/roles/', views.RolesUsuarioAPIView.as_view(), name='api_roles'),
    path('api/estadisticas/', views.EstadisticasAPIView.as_view(), name='api_estadisticas'),

    path('components/sidebar/', SidebarView.as_view(), name='sidebar-component'),
]