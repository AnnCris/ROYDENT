"""
Serializers para el sistema de autenticación - CORREGIDO
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Cliente, Proveedor, TipoCliente, Usuario, Persona, Rol, UsuarioRol
import re

class PersonaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Persona"""
    
    class Meta:
        model = Persona
        fields = [
            'id', 'nombre', 'apellido_paterno', 'apellido_materno',
            'cedula_identidad', 'numero_celular', 'correo',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def validate_nombre(self, value):
        """Validar nombre"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre es obligatorio")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres")
            
        if len(value.strip()) > 50:
            raise serializers.ValidationError("El nombre no puede tener más de 50 caracteres")
            
        if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', value.strip()):
            raise serializers.ValidationError("El nombre solo puede contener letras y espacios")
            
        return value.strip().title()

    def validate_apellido_paterno(self, value):
        """Validar apellido paterno"""
        if not value or not value.strip():
            raise serializers.ValidationError("El apellido paterno es obligatorio")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("El apellido paterno debe tener al menos 2 caracteres")
            
        if len(value.strip()) > 50:
            raise serializers.ValidationError("El apellido paterno no puede tener más de 50 caracteres")
            
        if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', value.strip()):
            raise serializers.ValidationError("El apellido paterno solo puede contener letras y espacios")
            
        return value.strip().title()

    def validate_apellido_materno(self, value):
        """Validar apellido materno (opcional)"""
        if value and value.strip():
            if len(value.strip()) < 2:
                raise serializers.ValidationError("El apellido materno debe tener al menos 2 caracteres")
                
            if len(value.strip()) > 50:
                raise serializers.ValidationError("El apellido materno no puede tener más de 50 caracteres")
                
            if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', value.strip()):
                raise serializers.ValidationError("El apellido materno solo puede contener letras y espacios")
                
            return value.strip().title()
        return value

    def validate_cedula_identidad(self, value):
        """Validar cédula de identidad boliviana"""
        if not value:
            raise serializers.ValidationError("La cédula de identidad es obligatoria")
        
        # Limpiar y formatear
        cedula_clean = value.strip().upper()
        
        # Validar formato específico boliviano
        if not re.match(r'^\d{7,8}(-[A-Z]{1,3})?$', cedula_clean):
            raise serializers.ValidationError(
                "Formato de cédula inválido. Ejemplos válidos: 1234567, 1234567-LP, 12345678-SC"
            )
        
        return cedula_clean

    def validate_numero_celular(self, value):
        """Validar número de celular boliviano"""
        if not value:
            raise serializers.ValidationError("El número de celular es obligatorio")
            
        # Limpiar espacios y caracteres especiales
        celular_clean = re.sub(r'[^\d]', '', value.strip())
        
        # Validar longitud exacta
        if len(celular_clean) != 8:
            raise serializers.ValidationError("El número de celular debe tener exactamente 8 dígitos")
        
        # Validar que empiece con 6 o 7
        if not celular_clean.startswith(('6', '7')):
            raise serializers.ValidationError("El número de celular debe empezar con 6 o 7")
            
        return celular_clean

    def validate_correo(self, value):
        """Validar correo electrónico"""
        if not value:
            raise serializers.ValidationError("El correo electrónico es obligatorio")
            
        # Validar formato básico
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value.strip().lower()):
            raise serializers.ValidationError("Formato de correo electrónico inválido")
            
        return value.strip().lower()

class RolSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Rol"""
    
    class Meta:
        model = Rol
        fields = ['id', 'nombre_rol', 'descripcion']

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Usuario"""
    persona = PersonaSerializer(read_only=True)
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre_usuario', 'persona', 'roles',
            'is_active', 'fecha_creacion', 'ultimo_login'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'ultimo_login']

    def get_roles(self, obj):
        """Obtener los roles activos del usuario"""
        roles_activos = obj.usuario_roles.filter(estado='ACTIVO')
        return [
            {
                'id': ur.rol.id,
                'nombre': ur.rol.nombre_rol,
                'descripcion': ur.rol.descripcion,
                'sucursal': ur.get_sucursal_asignada()
            }
            for ur in roles_activos
        ]

class LoginSerializer(serializers.Serializer):
    """Serializer para login"""
    nombre_usuario = serializers.CharField(
        max_length=150,
        error_messages={
            'required': 'El nombre de usuario es obligatorio',
            'blank': 'El nombre de usuario no puede estar vacío'
        }
    )
    password = serializers.CharField(
        write_only=True,
        error_messages={
            'required': 'La contraseña es obligatoria',
            'blank': 'La contraseña no puede estar vacía'
        }
    )

    def validate_nombre_usuario(self, value):
        """Validar nombre de usuario"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre de usuario es obligatorio")
        return value.strip()

    def validate_password(self, value):
        """Validar contraseña"""
        if not value:
            raise serializers.ValidationError("La contraseña es obligatoria")
        return value

    def validate(self, data):
        """Validar credenciales de login"""
        nombre_usuario = data.get('nombre_usuario')
        password = data.get('password')

        if not nombre_usuario or not password:
            raise serializers.ValidationError("Usuario y contraseña son obligatorios")

        # Buscar usuario por nombre_usuario
        try:
            usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")
        
        # Verificar contraseña
        if not usuario.check_password(password):
            raise serializers.ValidationError("Contraseña incorrecta")
            
        if not usuario.is_active:
            raise serializers.ValidationError("La cuenta está desactivada")

        data['usuario'] = usuario
        return data

class RegistroSerializer(serializers.Serializer):
    """Serializer para registro de usuarios con validaciones completas"""
    
    # Datos de persona
    nombre = serializers.CharField(max_length=50)
    apellido_paterno = serializers.CharField(max_length=50)
    apellido_materno = serializers.CharField(max_length=50, required=False, allow_blank=True)
    cedula_identidad = serializers.CharField(max_length=15)
    numero_celular = serializers.CharField(max_length=8)
    correo = serializers.EmailField()
    tipo_cliente_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Datos de usuario
    nombre_usuario = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)
    confirmar_password = serializers.CharField(write_only=True)
    
    # Rol (opcional, por defecto será CLIENTE)
    rol = serializers.CharField(required=False, default='CLIENTE')

    def validate_nombre(self, value):
        """Validar nombre"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre es obligatorio")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres")
            
        if len(value.strip()) > 50:
            raise serializers.ValidationError("El nombre no puede tener más de 50 caracteres")
            
        if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', value.strip()):
            raise serializers.ValidationError("El nombre solo puede contener letras y espacios")
            
        return value.strip().title()

    def validate_apellido_paterno(self, value):
        """Validar apellido paterno"""
        if not value or not value.strip():
            raise serializers.ValidationError("El apellido paterno es obligatorio")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("El apellido paterno debe tener al menos 2 caracteres")
            
        if len(value.strip()) > 50:
            raise serializers.ValidationError("El apellido paterno no puede tener más de 50 caracteres")
            
        if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', value.strip()):
            raise serializers.ValidationError("El apellido paterno solo puede contener letras y espacios")
            
        return value.strip().title()

    def validate_apellido_materno(self, value):
        """Validar apellido materno (opcional)"""
        if value and value.strip():
            if len(value.strip()) < 2:
                raise serializers.ValidationError("El apellido materno debe tener al menos 2 caracteres")
                
            if len(value.strip()) > 50:
                raise serializers.ValidationError("El apellido materno no puede tener más de 50 caracteres")
                
            if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', value.strip()):
                raise serializers.ValidationError("El apellido materno solo puede contener letras y espacios")
                
            return value.strip().title()
        return value or ''

    def validate_cedula_identidad(self, value):
        """Validar cédula de identidad"""
        if not value or not value.strip():
            raise serializers.ValidationError("La cédula de identidad es obligatoria")
            
        cedula_clean = value.strip().upper()
        
        if not re.match(r'^\d{7,8}(-[A-Z]{1,3})?$', cedula_clean):
            raise serializers.ValidationError(
                "Formato de cédula inválido. Ejemplos: 1234567, 1234567-LP, 12345678-SC"
            )
        
        # Verificar que no exista
        if Persona.objects.filter(cedula_identidad=cedula_clean).exists():
            raise serializers.ValidationError("Ya existe una persona registrada con esta cédula")
            
        return cedula_clean

    def validate_numero_celular(self, value):
        """Validar celular boliviano"""
        if not value or not value.strip():
            raise serializers.ValidationError("El número de celular es obligatorio")
            
        # Limpiar espacios y caracteres especiales
        celular_clean = re.sub(r'[^\d]', '', value.strip())
        
        # Validar longitud exacta
        if len(celular_clean) != 8:
            raise serializers.ValidationError("El número de celular debe tener exactamente 8 dígitos")
        
        # Validar que empiece con 6 o 7
        if not celular_clean.startswith(('6', '7')):
            raise serializers.ValidationError("El número de celular debe empezar con 6 o 7")
            
        return celular_clean

    def validate_nombre_usuario(self, value):
        """Validar que el nombre de usuario sea único y válido"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre de usuario es obligatorio")
            
        username_clean = value.strip().lower()
        
        # Validar longitud
        if len(username_clean) < 3:
            raise serializers.ValidationError("El nombre de usuario debe tener al menos 3 caracteres")
            
        if len(username_clean) > 20:
            raise serializers.ValidationError("El nombre de usuario no puede tener más de 20 caracteres")
        
        # Validar formato (letras, números, guiones y puntos)
        if not re.match(r'^[a-zA-Z0-9._-]+$', username_clean):
            raise serializers.ValidationError("El nombre de usuario solo puede contener letras, números, puntos, guiones y guiones bajos")
        
        # Verificar unicidad
        if Usuario.objects.filter(nombre_usuario__iexact=username_clean).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso")
            
        return username_clean

    def validate_correo(self, value):
        """Validar que el correo sea único"""
        if not value or not value.strip():
            raise serializers.ValidationError("El correo electrónico es obligatorio")
            
        # Validar formato
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value.strip().lower()):
            raise serializers.ValidationError("Formato de correo electrónico inválido")
            
        email_clean = value.strip().lower()
        
        # Verificar unicidad
        if Persona.objects.filter(correo__iexact=email_clean).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado")
            
        return email_clean

    def validate_password(self, value):
        """Validar fortaleza de contraseña"""
        if not value:
            raise serializers.ValidationError("La contraseña es obligatoria")
            
        if len(value) < 6:
            raise serializers.ValidationError("La contraseña debe tener al menos 6 caracteres")
            
        if len(value) > 128:
            raise serializers.ValidationError("La contraseña no puede tener más de 128 caracteres")
        
        # Verificar que contenga al menos una mayúscula
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra mayúscula")
        
        # Verificar que contenga al menos una minúscula
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra minúscula")
        
        # Verificar que contenga al menos un número
        if not re.search(r'\d', value):
            raise serializers.ValidationError("La contraseña debe contener al menos un número")
        
        # Verificar que contenga al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?\":{}|<>)")
        
        return value

    def validate(self, data):
        """Validaciones generales"""
        # Validar que las contraseñas coincidan
        if data['password'] != data['confirmar_password']:
            raise serializers.ValidationError({
                'confirmar_password': 'Las contraseñas no coinciden'
            })

        # Validar que el rol exista
        rol_nombre = data.get('rol', 'CLIENTE')
        if not Rol.objects.filter(nombre_rol=rol_nombre).exists():
            raise serializers.ValidationError({
                'rol': f'El rol {rol_nombre} no existe'
            })

        return data

    def create(self, validated_data):
        """Crear usuario y persona"""
        from django.db import transaction
        
        # Extraer datos
        confirmar_password = validated_data.pop('confirmar_password')
        password = validated_data.pop('password')
        rol_nombre = validated_data.pop('rol', 'CLIENTE')
        
        # Datos de persona
        datos_persona = {
            'nombre': validated_data['nombre'],
            'apellido_paterno': validated_data['apellido_paterno'],
            'apellido_materno': validated_data.get('apellido_materno', ''),
            'cedula_identidad': validated_data['cedula_identidad'],
            'numero_celular': validated_data['numero_celular'],
            'correo': validated_data['correo'],
        }
        
        # Datos de usuario
        nombre_usuario = validated_data['nombre_usuario']

        try:
            with transaction.atomic():
                # Crear persona
                persona = Persona.objects.create(**datos_persona)
                
                # Crear usuario
                usuario = Usuario.objects.create_user(
                    nombre_usuario=nombre_usuario,
                    password=password,
                    persona=persona
                )
                
                # Asignar rol
                rol = Rol.objects.get(nombre_rol=rol_nombre)
                UsuarioRol.objects.create(
                    usuario=usuario,
                    rol=rol,
                    estado='ACTIVO'
                )
                
                return usuario
                
        except Exception as e:
            raise serializers.ValidationError(f"Error al crear usuario: {str(e)}")

class CambiarPasswordSerializer(serializers.Serializer):
    """Serializer para cambiar contraseña"""
    password_actual = serializers.CharField(write_only=True)
    password_nueva = serializers.CharField(write_only=True, min_length=6)
    confirmar_password_nueva = serializers.CharField(write_only=True)

    def validate_password_nueva(self, value):
        """Validar nueva contraseña"""
        if len(value) < 6:
            raise serializers.ValidationError("La contraseña debe tener al menos 6 caracteres")
            
        # Aplicar las mismas validaciones que en registro
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra mayúscula")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra minúscula")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("La contraseña debe contener al menos un número")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos un carácter especial")
        
        return value

    def validate(self, data):
        """Validar cambio de contraseña"""
        usuario = self.context['request'].user
        
        # Verificar contraseña actual
        if not usuario.check_password(data['password_actual']):
            raise serializers.ValidationError({
                'password_actual': 'La contraseña actual es incorrecta'
            })
        
        # Verificar que las nuevas contraseñas coincidan
        if data['password_nueva'] != data['confirmar_password_nueva']:
            raise serializers.ValidationError({
                'confirmar_password_nueva': 'Las contraseñas no coinciden'
            })
        
        return data

    def save(self):
        """Cambiar la contraseña"""
        usuario = self.context['request'].user
        usuario.set_password(self.validated_data['password_nueva'])
        usuario.save()
        return usuario
    
# autenticacion/serializers.py - AGREGAR AL FINAL DEL ARCHIVO EXISTENTE

"""
Serializers para Clientes y Proveedores
"""

class TipoClienteSerializer(serializers.ModelSerializer):
    """Serializer para tipos de cliente"""
    
    class Meta:
        model = TipoCliente
        fields = ['id', 'codigo', 'nombre_tipo', 'descripcion']
        read_only_fields = ['id']


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer para clientes"""
    
    # Campos anidados de solo lectura
    nombre_completo = serializers.CharField(source='get_nombre_completo', read_only=True)
    documento = serializers.CharField(source='get_documento', read_only=True)
    tipo_cliente_nombre = serializers.CharField(source='tipo_cliente.nombre_tipo', read_only=True)
    email = serializers.EmailField(source='usuario.persona.correo', read_only=True)
    telefono = serializers.CharField(source='usuario.persona.numero_celular', read_only=True)
    cedula = serializers.CharField(source='usuario.persona.cedula_identidad', read_only=True)
    
    class Meta:
        model = Cliente
        fields = [
            'id',
            'usuario',
            'tipo_cliente',
            'tipo_cliente_nombre',
            'razon_social',
            'nit',
            'ciudad',
            'direccion',
            'especialidad',
            'estado',
            'es_vip',
            'limite_credito',
            'descuento_especial',
            'observaciones',
            'fecha_registro',
            'fecha_actualizacion',
            # Campos calculados
            'nombre_completo',
            'documento',
            'email',
            'telefono',
            'cedula',
        ]
        read_only_fields = ['id', 'fecha_registro', 'fecha_actualizacion']


class ClienteCreateSerializer(serializers.Serializer):
    """Serializer para crear un cliente nuevo (con usuario y persona)"""
    
    # Datos de Persona
    nombre = serializers.CharField(max_length=100)
    apellido_paterno = serializers.CharField(max_length=100)
    apellido_materno = serializers.CharField(max_length=100, required=False, allow_blank=True)
    cedula_identidad = serializers.CharField(max_length=15)
    numero_celular = serializers.CharField(max_length=8)
    correo = serializers.EmailField()
    
    # Datos de Usuario
    nombre_usuario = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    
    # Datos de Cliente
    tipo_cliente_id = serializers.IntegerField()
    razon_social = serializers.CharField(max_length=200, required=False, allow_blank=True)
    nit = serializers.CharField(max_length=20, required=False, allow_blank=True)
    ciudad = serializers.CharField(max_length=100, required=False, allow_blank=True)
    direccion = serializers.CharField(required=False, allow_blank=True)
    especialidad = serializers.CharField(max_length=200, required=False, allow_blank=True)
    observaciones = serializers.CharField(required=False, allow_blank=True)
    
    def validate_nombre_usuario(self, value):
        """Validar que el usuario no exista"""
        if Usuario.objects.filter(nombre_usuario=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya existe")
        return value
    
    def validate_cedula_identidad(self, value):
        """Validar que la cédula no exista"""
        if Persona.objects.filter(cedula_identidad=value).exists():
            raise serializers.ValidationError("Esta cédula ya está registrada")
        return value
    
    def validate_nit(self, value):
        """Validar que el NIT no exista si se proporciona"""
        if value and Cliente.objects.filter(nit=value).exists():
            raise serializers.ValidationError("Este NIT ya está registrado")
        return value
    
    def validate_tipo_cliente_id(self, value):
        """Validar que el tipo de cliente exista"""
        if not TipoCliente.objects.filter(id=value).exists():
            raise serializers.ValidationError("Tipo de cliente no válido")
        return value
    
    def create(self, validated_data):
        """Crear Persona + Usuario + Cliente"""
        from django.db import transaction
        
        with transaction.atomic():
            # 1. Crear Persona
            persona = Persona.objects.create(
                nombre=validated_data['nombre'],
                apellido_paterno=validated_data['apellido_paterno'],
                apellido_materno=validated_data.get('apellido_materno', ''),
                cedula_identidad=validated_data['cedula_identidad'],
                numero_celular=validated_data['numero_celular'],
                correo=validated_data['correo']
            )
            
            # 2. Crear Usuario
            usuario = Usuario.objects.create_user(
                nombre_usuario=validated_data['nombre_usuario'],
                password=validated_data['password'],
                persona=persona
            )
            
            # 3. Asignar rol CLIENTE
            rol_cliente = Rol.objects.get(nombre_rol='CLIENTE')
            UsuarioRol.objects.create(
                usuario=usuario,
                rol=rol_cliente,
                estado='ACTIVO'
            )
            
            # 4. Crear Cliente
            tipo_cliente = TipoCliente.objects.get(id=validated_data['tipo_cliente_id'])
            
            cliente = Cliente.objects.create(
                usuario=usuario,
                tipo_cliente=tipo_cliente,
                razon_social=validated_data.get('razon_social', ''),
                nit=validated_data.get('nit', ''),
                ciudad=validated_data.get('ciudad', ''),
                direccion=validated_data.get('direccion', ''),
                especialidad=validated_data.get('especialidad', ''),
                observaciones=validated_data.get('observaciones', ''),
                estado='ACTIVO'
            )
            
            return cliente


class ProveedorSerializer(serializers.ModelSerializer):
    """Serializer para proveedores"""
    
    class Meta:
        model = Proveedor
        fields = [
            'id',
            'nombre',
            'nit',
            'tipo_proveedor',
            'telefono',
            'email',
            'pais',
            'ciudad',
            'direccion',
            'persona_contacto',
            'cargo_contacto',
            'condiciones_pago',
            'dias_credito',
            'calificacion',
            'estado',
            'es_premium',
            'observaciones',
            'fecha_registro',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_registro', 'fecha_actualizacion']
    
    def validate_nit(self, value):
        """Validar que el NIT sea único (excepto en actualización)"""
        if self.instance:  # Actualización
            if Proveedor.objects.exclude(id=self.instance.id).filter(nit=value).exists():
                raise serializers.ValidationError("Este NIT ya está registrado")
        else:  # Creación
            if Proveedor.objects.filter(nit=value).exists():
                raise serializers.ValidationError("Este NIT ya está registrado")
        return value
    
    def validate_calificacion(self, value):
        """Validar que la calificación esté entre 0 y 5"""
        if value < 0 or value > 5:
            raise serializers.ValidationError("La calificación debe estar entre 0 y 5")
        return value