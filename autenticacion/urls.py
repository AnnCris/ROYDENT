"""
URLs para la aplicación de autenticación - Con CRUD de usuarios
"""
from django.urls import path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

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
    
    # ============ CRUD DE USUARIOS ============
    path('api/usuarios/', views.listar_usuarios, name='api_listar_usuarios'),
    path('api/usuarios/<int:usuario_id>/', views.obtener_usuario, name='api_obtener_usuario'),
    path('api/usuarios/crear/', views.crear_usuario, name='api_crear_usuario'),
    path('api/usuarios/<int:usuario_id>/actualizar/', views.actualizar_usuario, name='api_actualizar_usuario'),
    path('api/usuarios/<int:usuario_id>/eliminar/', views.eliminar_usuario, name='api_eliminar_usuario'),
    path('api/usuarios/<int:usuario_id>/activar/', views.activar_usuario, name='api_activar_usuario'),
    path('api/usuarios/estadisticas/', views.estadisticas_usuarios, name='api_estadisticas_usuarios'),
    
    # Utilidades
    path('api/roles/', views.RolesUsuarioAPIView.as_view(), name='api_roles'),
    path('api/estadisticas/', views.EstadisticasAPIView.as_view(), name='api_estadisticas'),
]