"""
Script para crear superusuario con modelo personalizado
"""
import os
import django
import getpass

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roy_representaciones.settings')
django.setup()

from django.db import transaction
from autenticacion.models import Persona, Usuario, Rol, UsuarioRol

def crear_superusuario():
    print('\n=== CREACIÓN DE SUPERUSUARIO ===\n')
    
    # Datos de la persona
    print('📋 DATOS PERSONALES')
    nombre = input('Nombre: ').strip()
    apellido_paterno = input('Apellido Paterno: ').strip()
    apellido_materno = input('Apellido Materno (opcional): ').strip() or None
    cedula = input('Cédula de Identidad (ej: 1234567-LP): ').strip()
    celular = input('Número de Celular (opcional, 8 dígitos): ').strip() or None
    correo = input('Correo Electrónico (opcional): ').strip() or None
    
    # Datos del usuario
    print('\n👤 DATOS DE USUARIO')
    nombre_usuario = input('Nombre de Usuario: ').strip()
    
    # Verificar si ya existe
    if Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
        print(f'❌ Error: El usuario "{nombre_usuario}" ya existe.')
        return
    
    # Contraseña
    while True:
        password = getpass.getpass('Contraseña: ')
        password_confirm = getpass.getpass('Confirmar Contraseña: ')
        
        if password == password_confirm:
            if len(password) < 6:
                print('❌ La contraseña debe tener al menos 6 caracteres.')
                continue
            break
        else:
            print('❌ Las contraseñas no coinciden.')
    
    try:
        with transaction.atomic():
            # Crear persona
            persona = Persona.objects.create(
                nombre=nombre,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                cedula_identidad=cedula,
                numero_celular=celular,
                correo=correo
            )
            print(f'✅ Persona creada: {persona.get_nombre_completo()}')
            
            # Crear usuario
            usuario = Usuario.objects.create_superuser(
                nombre_usuario=nombre_usuario,
                password=password,
                persona=persona
            )
            print(f'✅ Usuario creado: {nombre_usuario}')
            
            # Crear o obtener rol de Administrador
            rol_admin, created = Rol.objects.get_or_create(
                nombre_rol='ADMINISTRADOR',
                defaults={
                    'descripcion': 'Administrador del sistema con acceso total'
                }
            )
            if created:
                print('✅ Rol de Administrador creado')
            
            # Asignar rol al usuario
            UsuarioRol.objects.create(
                usuario=usuario,
                rol=rol_admin,
                estado='ACTIVO'
            )
            print('✅ Rol asignado al usuario')
            
            print('\n🎉 ¡SUPERUSUARIO CREADO EXITOSAMENTE!\n')
            print(f'👤 Usuario: {nombre_usuario}')
            print(f'👨 Persona: {persona.get_nombre_completo()}')
            print(f'🔐 CI: {cedula}')
            print(f'🎭 Rol: Administrador\n')
            
    except Exception as e:
        print(f'\n❌ Error al crear superusuario: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    crear_superusuario()