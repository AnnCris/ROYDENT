from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import Cliente, Persona, Proveedor, TipoCliente, Usuario, Rol, UsuarioRol, Permiso, RolPermiso


# ============= FORMULARIOS PERSONALIZADOS =============

class PersonaAdminForm(forms.ModelForm):
    """Formulario personalizado para Persona en el admin"""
    class Meta:
        model = Persona
        fields = '__all__'

class UsuarioCreationForm(forms.ModelForm):
    """Formulario para crear usuarios"""
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ('nombre_usuario', 'persona')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password1"])
        if commit:
            usuario.save()
        return usuario


class UsuarioChangeForm(forms.ModelForm):
    """Formulario para actualizar usuarios"""
    password = ReadOnlyPasswordHashField(
        label="Contraseña",
        help_text=(
            "Las contraseñas no se almacenan en texto plano, por lo que no hay forma de ver "
            "la contraseña de este usuario, pero puedes cambiarla usando "
            "<a href=\"../password/\">este formulario</a>."
        ),
    )

    class Meta:
        model = Usuario
        fields = '__all__'


# ============= INLINE PARA RELACIONES =============

class UsuarioRolInline(admin.TabularInline):
    model = UsuarioRol
    extra = 1
    verbose_name = "Rol del Usuario"
    verbose_name_plural = "Roles del Usuario"


class RolPermisoInline(admin.TabularInline):
    model = RolPermiso
    extra = 1
    verbose_name = "Permiso del Rol"
    verbose_name_plural = "Permisos del Rol"


# ============= ADMIN MODELS =============

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    form = PersonaAdminForm
    list_display = ('cedula_identidad', 'nombre', 'apellido_paterno', 'apellido_materno', 
                    'numero_celular', 'correo', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('nombre', 'apellido_paterno', 'apellido_materno', 'cedula_identidad', 
                     'numero_celular', 'correo')
    ordering = ('-fecha_creacion',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido_paterno', 'apellido_materno')
        }),
        ('Documentación', {
            'fields': ('cedula_identidad',)
        }),
        ('Contacto', {
            'fields': ('numero_celular', 'correo')
        }),
    )


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    
    list_display = ('nombre_usuario', 'get_nombre_completo', 'is_active', 'is_staff', 
                    'is_superuser', 'fecha_creacion')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'fecha_creacion')
    
    fieldsets = (
        (None, {'fields': ('nombre_usuario', 'password')}),
        ('Información Personal', {'fields': ('persona',)}),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Fechas Importantes', {'fields': ('ultimo_login', 'fecha_creacion')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nombre_usuario', 'persona', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'ultimo_login')
    search_fields = ('nombre_usuario', 'persona__nombre', 'persona__apellido_paterno')
    ordering = ('-fecha_creacion',)
    filter_horizontal = ()
    inlines = [UsuarioRolInline]
    
    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()
    get_nombre_completo.short_description = 'Nombre Completo'


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre_rol', 'descripcion', 'fecha_creacion')
    list_filter = ('nombre_rol', 'fecha_creacion')
    search_fields = ('nombre_rol', 'descripcion')
    ordering = ('nombre_rol',)
    inlines = [RolPermisoInline]
    
    fieldsets = (
        ('Información del Rol', {
            'fields': ('nombre_rol', 'descripcion')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'estado', 'fecha_asignacion')
    list_filter = ('rol', 'estado', 'fecha_asignacion')
    search_fields = ('usuario__nombre_usuario', 'rol__nombre_rol')
    ordering = ('-fecha_asignacion',)
    
    fieldsets = (
        ('Asignación', {
            'fields': ('usuario', 'rol', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_asignacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('fecha_asignacion', 'fecha_actualizacion')


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ('codigo_permiso', 'nombre_permiso', 'modulo', 'tipo_permiso', 'fecha_creacion')
    list_filter = ('modulo', 'tipo_permiso', 'fecha_creacion')
    search_fields = ('nombre_permiso', 'codigo_permiso', 'descripcion')
    ordering = ('modulo', 'tipo_permiso')
    
    fieldsets = (
        ('Información del Permiso', {
            'fields': ('nombre_permiso', 'codigo_permiso', 'modulo', 'tipo_permiso', 'descripcion')
        }),
    )
    readonly_fields = ('fecha_creacion',)


@admin.register(RolPermiso)
class RolPermisoAdmin(admin.ModelAdmin):
    list_display = ('rol', 'permiso', 'asignado_por', 'fecha_asignacion')
    list_filter = ('rol', 'permiso__modulo', 'fecha_asignacion')
    search_fields = ('rol__nombre_rol', 'permiso__nombre_permiso')
    ordering = ('-fecha_asignacion',)
    
    fieldsets = (
        ('Asignación de Permiso', {
            'fields': ('rol', 'permiso', 'asignado_por')
        }),
    )
    readonly_fields = ('fecha_asignacion',)

# autenticacion/admin.py - AGREGAR AL FINAL DEL ARCHIVO EXISTENTE

"""
Admin para Clientes y Proveedores
"""

# ============= TIPO DE CLIENTE =============

@admin.register(TipoCliente)
class TipoClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_tipo', 'codigo', 'fecha_creacion')
    list_filter = ('codigo',)
    search_fields = ('nombre_tipo', 'codigo', 'descripcion')
    ordering = ('nombre_tipo',)
    readonly_fields = ('fecha_creacion',)
    
    fieldsets = (
        ('Información del Tipo', {
            'fields': ('codigo', 'nombre_tipo', 'descripcion')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )


# ============= CLIENTE =============

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'get_nombre_completo',
        'tipo_cliente',
        'nit',
        'estado',
        'fecha_registro'
    )
    
    list_filter = (
        'estado',
        'tipo_cliente',
        'fecha_registro'
    )
    
    search_fields = (
        'usuario__persona__nombre',
        'usuario__persona__apellido_paterno',
        'usuario__persona__cedula_identidad',
        'razon_social',
        'nit',
        'usuario__persona__correo'
    )
    
    readonly_fields = ('fecha_registro', 'fecha_actualizacion')
    autocomplete_fields = ['usuario', 'tipo_cliente']
    
    fieldsets = (
        ('Usuario Asociado', {
            'fields': ('usuario',)
        }),
        ('Tipo de Cliente', {
            'fields': ('tipo_cliente',)
        }),
        ('Información Comercial', {
            'fields': ('razon_social', 'nit')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()
    get_nombre_completo.short_description = 'Cliente'


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = (
        'get_nombre_completo',
        'nit',
        'tipo_proveedor',
        'estado',
        'fecha_registro'
    )
    
    list_filter = (
        'estado',
        'tipo_proveedor',
        'fecha_registro'
    )
    
    search_fields = (
        'persona__nombre',
        'persona__apellido_paterno',
        'persona__cedula_identidad',
        'nit',
        'razon_social',
        'persona__correo'
    )
    
    readonly_fields = ('fecha_registro', 'fecha_actualizacion')
    autocomplete_fields = ['persona']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('persona',)
        }),
        ('Información Comercial', {
            'fields': ('tipo_proveedor', 'nit', 'razon_social')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()
    get_nombre_completo.short_description = 'Proveedor'
