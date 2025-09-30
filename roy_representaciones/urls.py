"""
URLs principales del Sistema Roy Representaciones - Versión simplificada
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Administración de Django
    path('admin/', admin.site.urls),
    
    # Página principal - index.html de Roy Dent
    path('', TemplateView.as_view(template_name='index.html'), name='index'),

    # Sistema de autenticación
    path('auth/', include('autenticacion.urls')),

    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('registro/', TemplateView.as_view(template_name='registro.html'), name='registro'),
    path('panel-admin/', TemplateView.as_view(template_name='panel-admin.html'), name='panel-admin'),
    path('panel-mundomedico/', TemplateView.as_view(template_name='panel-mundomedico.html'), name='panel-mundomedico'),
    path('panel-roydent/', TemplateView.as_view(template_name='panel-roydent.html'), name='panel-roydent'),
    path('catalogo/', TemplateView.as_view(template_name='catalogo.html'), name='catalogo'),

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