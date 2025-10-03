"""
Modelos para el sistema de autenticación de Roy Representaciones
Estructura basada en la realidad boliviana
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
import re

class Persona(models.Model):
    """
    Modelo base para personas en el sistema
    """
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido_paterno = models.CharField(max_length=100, verbose_name="Apellido Paterno")
    apellido_materno = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apellido Materno")
    
    # Validador para cédula de identidad boliviana
    cedula_validator = RegexValidator(
        regex=r'^\d{7,8}(-[A-Z]{1,2})?$',
        message='Formato de cédula inválido. Ejemplo: 1234567 o 1234567-LP'
    )
    cedula_identidad = models.CharField(
        max_length=15, 
        unique=True, 
        validators=[cedula_validator],
        verbose_name="Cédula de Identidad"
    )
    
    # Validador para números de celular bolivianos
    celular_validator = RegexValidator(
        regex=r'^[67]\d{7}$',
        message='Número de celular inválido. Debe empezar con 6 o 7 y tener 8 dígitos.'
    )
    numero_celular = models.CharField(
        max_length=8, 
        validators=[celular_validator],
        blank=True, 
        null=True,
        verbose_name="Número de Celular"
    )
    
    correo = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        db_table = "persona"

    def __str__(self):
        nombre_completo = f"{self.nombre} {self.apellido_paterno}"
        if self.apellido_materno:
            nombre_completo += f" {self.apellido_materno}"
        return nombre_completo

    def get_nombre_completo(self):
        """Retorna el nombre completo de la persona"""
        return self.__str__()

    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError
        
        # Validar formato de cédula más específico
        if self.cedula_identidad:
            cedula_clean = self.cedula_identidad.strip().upper()
            
            # Patrón más específico para cédulas bolivianas
            if not re.match(r'^\d{7,8}(-[A-Z]{1,3})?$', cedula_clean):
                raise ValidationError({
                    'cedula_identidad': 'Formato de cédula inválido. Ejemplos válidos: 1234567, 1234567-LP, 12345678-SC'
                })
            
            self.cedula_identidad = cedula_clean

class Rol(models.Model):
    """
    Roles del sistema Roy Representaciones
    """
    ROLES_CHOICES = [
        ('ADMINISTRADOR', 'Administrador del Sistema'),
        ('VENDEDOR_ROYDENT', 'Vendedor RoyDent'),
        ('VENDEDOR_MUNDO_MEDICO', 'Vendedor Mundo Médico'),
        ('CLIENTE', 'Cliente'),
    ]
    
    nombre_rol = models.CharField(
        max_length=50, 
        choices=ROLES_CHOICES,
        unique=True, 
        verbose_name="Nombre del Rol"
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        db_table = "rol"

    def __str__(self):
        return self.get_nombre_rol_display()

class UsuarioManager(BaseUserManager):
    """
    Manager personalizado para el modelo Usuario
    """
    def create_user(self, nombre_usuario, password=None, persona=None, **extra_fields):
        """Crear usuario normal"""
        if not nombre_usuario:
            raise ValueError('El nombre de usuario es obligatorio')
        
        if not persona:
            raise ValueError('La persona es obligatoria para crear un usuario')
        
        usuario = self.model(
            nombre_usuario=nombre_usuario, 
            persona=persona,
            **extra_fields
        )
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, nombre_usuario, password=None, persona=None, **extra_fields):
        """Crear superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(nombre_usuario, password, persona=persona, **extra_fields)
    
class Usuario(AbstractBaseUser):
    """
    Modelo de Usuario personalizado para Roy Representaciones
    """
    persona = models.OneToOneField(
        Persona, 
        on_delete=models.CASCADE, 
        related_name='usuario',
        verbose_name="Persona"
    )
    nombre_usuario = models.CharField(
        max_length=150, 
        unique=True, 
        verbose_name="Nombre de Usuario"
    )
    password = models.CharField(max_length=128, verbose_name="Contraseña")
    
    # Campos requeridos por Django
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False, verbose_name="Es Staff")
    is_superuser = models.BooleanField(default=False, verbose_name="Es Superusuario")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    ultimo_login = models.DateTimeField(blank=True, null=True, verbose_name="Último Login")

    objects = UsuarioManager()

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        db_table = "usuario"

    def __str__(self):
        return f"{self.nombre_usuario} ({self.persona.get_nombre_completo()})"

    def get_nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        return self.persona.get_nombre_completo()

    def has_perm(self, perm, obj=None):
        """Permisos del usuario"""
        return True

    def has_module_perms(self, app_label):
        """Permisos de módulo"""
        return True

    @property
    def email(self):
        """Propiedad para compatibilidad con sistemas que esperan email"""
        return self.persona.correo

class UsuarioRol(models.Model):
    """
    Relación Many-to-Many entre Usuario y Rol
    Permite que un usuario tenga múltiples roles
    """
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]
    
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='usuario_roles',
        verbose_name="Usuario"
    )
    rol = models.ForeignKey(
        Rol, 
        on_delete=models.CASCADE, 
        related_name='rol_usuarios',
        verbose_name="Rol"
    )
    estado = models.CharField(
        max_length=10, 
        choices=ESTADO_CHOICES,
        default='ACTIVO',
        verbose_name="Estado"
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Asignación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Usuario Rol"
        verbose_name_plural = "Usuario Roles"
        db_table = "usuario_rol"
        unique_together = ('usuario', 'rol')

    def __str__(self):
        return f"{self.usuario.nombre_usuario} - {self.rol.nombre_rol} ({self.estado})"

    def get_sucursal_asignada(self):
        """
        Retorna la sucursal asignada según el rol
        """
        sucursales = {
            'ADMINISTRADOR': 'deposito',
            'VENDEDOR_ROYDENT': 'roydent',
            'VENDEDOR_MUNDO_MEDICO': 'mundo_medico',
            'CLIENTE': None
        }
        return sucursales.get(self.rol.nombre_rol)
    
    # Agregar estas clases al final de tu archivo autenticacion/models.py

class Permiso(models.Model):
    """
    Permisos específicos del sistema
    """
    TIPO_PERMISO_CHOICES = [
        ('VER', 'Ver/Listar'),
        ('CREAR', 'Crear'),
        ('EDITAR', 'Editar'),
        ('ELIMINAR', 'Eliminar'),
        ('EXPORTAR', 'Exportar'),
        ('IMPORTAR', 'Importar'),
    ]
    
    MODULO_CHOICES = [
        ('PRODUCTOS', 'Productos'),
        ('INVENTARIO', 'Inventario'),
        ('VENTAS', 'Ventas'),
        ('TRANSFERENCIAS', 'Transferencias'),
        ('CLIENTES', 'Clientes'),
        ('REPORTES', 'Reportes'),
        ('USUARIOS', 'Usuarios'),
        ('CONFIGURACION', 'Configuración'),
    ]
    
    nombre_permiso = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Permiso")
    codigo_permiso = models.CharField(max_length=50, unique=True, verbose_name="Código")
    modulo = models.CharField(max_length=50, choices=MODULO_CHOICES, verbose_name="Módulo")
    tipo_permiso = models.CharField(max_length=20, choices=TIPO_PERMISO_CHOICES, verbose_name="Tipo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
        db_table = "permiso"
        unique_together = ('modulo', 'tipo_permiso')
    
    def __str__(self):
        return f"{self.get_modulo_display()} - {self.get_tipo_permiso_display()}"

class RolPermiso(models.Model):
    """
    Relación entre Roles y Permisos
    """
    rol = models.ForeignKey(
        Rol, 
        on_delete=models.CASCADE, 
        related_name='rol_permisos',
        verbose_name="Rol"
    )
    permiso = models.ForeignKey(
        Permiso, 
        on_delete=models.CASCADE, 
        related_name='permiso_roles',
        verbose_name="Permiso"
    )
    asignado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='permisos_asignados',
        verbose_name="Asignado Por"
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Asignación")
    
    class Meta:
        verbose_name = "Rol Permiso"
        verbose_name_plural = "Roles Permisos"
        db_table = "rol_permiso"
        unique_together = ('rol', 'permiso')
    
    def __str__(self):
        return f"{self.rol.nombre_rol} - {self.permiso.nombre_permiso}"
    

# autenticacion/models.py - AGREGAR AL FINAL DEL ARCHIVO EXISTENTE

"""
Modelos para Clientes y Proveedores
Los clientes usan Persona + Usuario con rol CLIENTE
Los proveedores son entidades independientes sin acceso al sistema
"""

class TipoCliente(models.Model):
    """
    Tipos predefinidos de clientes según su profesión/ocupación
    """
    TIPOS_PREDEFINIDOS = [
        ('ODONTOLOGO', 'Odontólogo'),
        ('MEDICO', 'Médico'),
        ('EST_ODONTOLOGIA', 'Estudiante Odontología'),
        ('EST_MEDICINA', 'Estudiante Medicina'),
        ('EST_ENFERMERIA', 'Estudiante Enfermería'),
        ('EST_VETERINARIA', 'Estudiante Veterinaria'),
        ('ENFERMERO', 'Enfermero/a'),
        ('VETERINARIO', 'Veterinario/a'),
        ('LAB_DENTAL', 'Laboratorio Dental'),
    ]
    
    codigo = models.CharField(
        max_length=50,
        choices=TIPOS_PREDEFINIDOS,
        unique=True,
        verbose_name="Código"
    )
    nombre_tipo = models.CharField(max_length=100, verbose_name="Nombre del Tipo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Tipo de Cliente"
        verbose_name_plural = "Tipos de Cliente"
        db_table = "tipo_cliente"
        ordering = ['nombre_tipo']
    
    def __str__(self):
        return self.nombre_tipo


class Cliente(models.Model):
    """
    Cliente del sistema - Extiende el modelo Usuario con rol CLIENTE
    Los clientes tienen acceso limitado al catálogo de productos
    """
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('VIP', 'VIP'),
        ('SUSPENDIDO', 'Suspendido'),
    ]
    
    # Relación uno a uno con Usuario (que ya tiene Persona)
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='cliente',
        verbose_name="Usuario"
    )
    
    # Información específica del cliente
    tipo_cliente = models.ForeignKey(
        TipoCliente,
        on_delete=models.PROTECT,
        related_name='clientes',
        verbose_name="Tipo de Cliente"
    )
    
    razon_social = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Razón Social",
        help_text="Para clínicas, laboratorios o empresas"
    )
    
    nit = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name="NIT",
        help_text="Para facturación"
    )
    
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ciudad"
    )
    
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Dirección"
    )
    
    especialidad = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Especialidad"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ACTIVO',
        verbose_name="Estado"
    )
    
    es_vip = models.BooleanField(
        default=False,
        verbose_name="Cliente VIP"
    )
    
    limite_credito = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Límite de Crédito (Bs.)"
    )
    
    descuento_especial = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Descuento Especial (%)",
        help_text="Porcentaje de descuento adicional"
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Registro"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        db_table = "cliente"
        ordering = ['-fecha_registro']
    
    def __str__(self):
        if self.razon_social:
            return f"{self.razon_social} - {self.usuario.persona.get_nombre_completo()}"
        return self.usuario.persona.get_nombre_completo()
    
    def get_nombre_completo(self):
        """Retorna el nombre completo o razón social"""
        if self.razon_social:
            return self.razon_social
        return self.usuario.persona.get_nombre_completo()
    
    def get_documento(self):
        """Retorna NIT o CI según corresponda"""
        if self.nit:
            return f"NIT: {self.nit}"
        return f"CI: {self.usuario.persona.cedula_identidad}"
    
    def total_compras(self):
        """Calcula el total de compras del cliente"""
        # Placeholder - implementar cuando tengamos el módulo de ventas
        return 0.00
    
    def puede_comprar(self):
        """Verifica si el cliente puede realizar compras"""
        return self.estado in ['ACTIVO', 'VIP'] and self.usuario.is_active


class Proveedor(models.Model):
    """
    Proveedor de productos médicos y odontológicos
    Los proveedores NO tienen acceso al sistema
    """
    TIPO_PROVEEDOR = [
        ('DISTRIBUIDOR', 'Distribuidor'),
        ('FABRICANTE', 'Fabricante'),
        ('IMPORTADOR', 'Importador'),
        ('MAYORISTA', 'Mayorista'),
        ('MINORISTA', 'Minorista'),
    ]
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('PREMIUM', 'Premium'),
        ('SUSPENDIDO', 'Suspendido'),
    ]
    
    # Información básica
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre / Razón Social"
    )
    
    nit = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="NIT"
    )
    
    tipo_proveedor = models.CharField(
        max_length=20,
        choices=TIPO_PROVEEDOR,
        default='DISTRIBUIDOR',
        verbose_name="Tipo de Proveedor"
    )
    
    # Contacto
    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono"
    )
    
    email = models.EmailField(
        verbose_name="Email"
    )
    
    pais = models.CharField(
        max_length=100,
        default='Bolivia',
        verbose_name="País"
    )
    
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ciudad"
    )
    
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Dirección"
    )
    
    # Persona de contacto
    persona_contacto = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Persona de Contacto"
    )
    
    cargo_contacto = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cargo"
    )
    
    # Condiciones comerciales
    condiciones_pago = models.CharField(
        max_length=100,
        default='Contado',
        verbose_name="Condiciones de Pago"
    )
    
    dias_credito = models.IntegerField(
        default=0,
        verbose_name="Días de Crédito"
    )
    
    calificacion = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        verbose_name="Calificación (0-5)",
        help_text="Calificación del proveedor"
    )
    
    # Estado y control
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ACTIVO',
        verbose_name="Estado"
    )
    
    es_premium = models.BooleanField(
        default=False,
        verbose_name="Proveedor Premium"
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Registro"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        db_table = "proveedor"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.nit}"
    
    def total_compras(self):
        """Calcula el total de compras realizadas a este proveedor"""
        # Placeholder - implementar cuando tengamos el módulo de compras
        return 0.00
    
    def promedio_tiempo_entrega(self):
        """Calcula el promedio de días de entrega"""
        # Placeholder - implementar cuando tengamos el módulo de compras
        return 0
    
    def productos_suministrados(self):
        """Cantidad de productos que suministra este proveedor"""
        # Placeholder - implementar cuando tengamos el módulo de productos
        return 0