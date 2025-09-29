"""
Configuración del admin para autenticacion
"""
from django.contrib import admin
from .models import Persona, Usuario, Rol, UsuarioRol

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = [
        'cedula_identidad', 'nombre', 'apellido_paterno', 
        'apellido_materno', 'correo', 'numero_celular'
    ]
    list_filter = ['fecha_creacion']
    search_fields = ['nombre', 'apellido_paterno', 'cedula_identidad', 'correo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido_paterno', 'apellido_materno')
        }),
        ('Documentos de Identidad', {
            'fields': ('cedula_identidad',)
        }),
        ('Contacto', {
            'fields': ('correo', 'numero_celular')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre_rol', 'descripcion', 'fecha_creacion']
    list_filter = ['nombre_rol', 'fecha_creacion']
    search_fields = ['nombre_rol', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

class UsuarioRolInline(admin.TabularInline):
    model = UsuarioRol
    extra = 1
    readonly_fields = ['fecha_asignacion', 'fecha_actualizacion']

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'nombre_usuario', 'get_nombre_completo', 'get_cedula',
        'get_correo', 'is_active', 'fecha_creacion'
    ]
    list_filter = ['is_active', 'is_staff', 'fecha_creacion']
    search_fields = [
        'nombre_usuario', 'persona__nombre', 'persona__apellido_paterno',
        'persona__cedula_identidad', 'persona__correo'
    ]
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'ultimo_login']
    ordering = ['nombre_usuario']
    
    fieldsets = (
        ('Información de Usuario', {
            'fields': ('nombre_usuario', 'password')
        }),
        ('Información Personal', {
            'fields': ('persona',)
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Fechas Importantes', {
            'fields': ('ultimo_login', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [UsuarioRolInline]
    
    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()
    get_nombre_completo.short_description = 'Nombre Completo'
    
    def get_cedula(self, obj):
        return obj.persona.cedula_identidad
    get_cedula.short_description = 'Cédula'
    
    def get_correo(self, obj):
        return obj.persona.correo
    get_correo.short_description = 'Correo'

@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'rol', 'estado', 'get_sucursal',
        'fecha_asignacion'
    ]
    list_filter = ['rol', 'estado', 'fecha_asignacion']
    search_fields = [
        'usuario__nombre_usuario', 'usuario__persona__nombre',
        'rol__nombre_rol'
    ]
    readonly_fields = ['fecha_asignacion', 'fecha_actualizacion']
    
    def get_sucursal(self, obj):
        return obj.get_sucursal_asignada() or 'N/A'
    get_sucursal.short_description = 'Sucursal'