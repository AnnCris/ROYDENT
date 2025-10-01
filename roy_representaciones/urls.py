"""
URLs principales del Sistema Roy Representaciones - Versión simplificada
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

class ProtectedTemplateView(TemplateView):
    """Vista que requiere autenticación"""
    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        return login_required(view, login_url='/login/')
    
urlpatterns = [
    # Administración de Django
    path('admin/', admin.site.urls),
    
    # Página principal - index.html de Roy Dent
    path('', TemplateView.as_view(template_name='index.html'), name='index'),

    # Sistema de autenticación
    path('auth/', include('autenticacion.urls')),

    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('registro/', TemplateView.as_view(template_name='registro.html'), name='registro'),

    # ============ PANELES PROTEGIDOS - REQUIEREN LOGIN ============
    path('panel-admin/', ProtectedTemplateView.as_view(template_name='panel-admin.html'), name='panel-admin'),
    path('panel-mundomedico/', ProtectedTemplateView.as_view(template_name='panel-mundomedico.html'), name='panel-mundomedico'),
    path('panel-roydent/', ProtectedTemplateView.as_view(template_name='panel-roydent.html'), name='panel-roydent'),
    
    # Catálogo - PROTEGIDO
    path('catalogo/', ProtectedTemplateView.as_view(template_name='catalogo.html'), name='catalogo'),
    
    # Gestión de usuarios - PROTEGIDO
    path('gestionusuario/', ProtectedTemplateView.as_view(template_name='gestionusuario.html'), name='gestionusuario'),
    
    # ============ COMPONENTE SIDEBAR ============
    path('components/sidebar/', TemplateView.as_view(template_name='components/sidebar.html'), name='sidebar-component'),
]

# Servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizar textos del admin
admin.site.site_header = 'Roy Representaciones - Sistema de Gestión'
admin.site.site_title = 'Roy Representaciones'
admin.site.index_title = 'Panel de Administración'