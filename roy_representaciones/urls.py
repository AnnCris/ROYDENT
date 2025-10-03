"""
URLs principales del Sistema Roy Representaciones - Versión completa
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from autenticacion import views

class ProtectedTemplateView(TemplateView):
    """Vista que requiere autenticación"""
    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        return login_required(view, login_url='/login/')
    
urlpatterns = [
    # ============ ADMINISTRACIÓN DE DJANGO ============
    path('admin/', admin.site.urls),
    
    # ============ PÁGINAS PÚBLICAS ============
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('registro/', TemplateView.as_view(template_name='registro.html'), name='registro'),

    # ============ SISTEMA DE AUTENTICACIÓN ============
    path('auth/', include('autenticacion.urls')),

    # ============ PANELES PROTEGIDOS - REQUIEREN LOGIN ============
    path('panel-admin/', ProtectedTemplateView.as_view(template_name='panel-admin.html'), name='panel-admin'),
    path('panel-mundomedico/', ProtectedTemplateView.as_view(template_name='panel-mundomedico.html'), name='panel-mundomedico'),
    path('panel-roydent/', ProtectedTemplateView.as_view(template_name='panel-roydent.html'), name='panel-roydent'),
    
    # ============ GESTIÓN PROTEGIDA ============
    # Catálogo
    path('catalogo/', ProtectedTemplateView.as_view(template_name='catalogo.html'), name='catalogo'),
    
    # Gestión de Usuarios
    path('gestionusuario/', ProtectedTemplateView.as_view(template_name='gestionusuario.html'), name='gestionusuario'),
    
    # Gestión de Clientes
    path('gestionclientes/', ProtectedTemplateView.as_view(template_name='gestionclientes.html'), name='gestionclientes'),
    
    # Gestión de Proveedores
    path('gestionproveedores/', ProtectedTemplateView.as_view(template_name='gestionproveedores.html'), name='gestionproveedores'),
    
    # ============ COMPONENTES ============
    path('components/sidebar/', TemplateView.as_view(template_name='components/sidebar.html'), name='sidebar-component'),

    # ============ APIs DE PERMISOS ============
    path('api/permisos/', views.listar_permisos, name='api_listar_permisos'),
    path('api/usuarios/<int:usuario_id>/permisos/', views.obtener_permisos_usuario, name='api_permisos_usuario'),
    path('api/usuarios/<int:usuario_id>/permisos/actualizar/', views.actualizar_permisos_usuario, name='api_actualizar_permisos_usuario'),
    path('api/roles/permisos/', views.matriz_permisos_roles, name='api_matriz_permisos'),

    
]

# ============ ARCHIVOS MEDIA Y STATIC EN DESARROLLO ============
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ============ PERSONALIZACIÓN DEL ADMIN ============
admin.site.site_header = 'Roy Representaciones - Sistema de Gestión'
admin.site.site_title = 'Roy Representaciones'
admin.site.index_title = 'Panel de Administración'