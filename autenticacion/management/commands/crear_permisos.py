"""
Management command para crear permisos iniciales del sistema
"""
from django.core.management.base import BaseCommand
from autenticacion.models import Permiso, Rol, RolPermiso

class Command(BaseCommand):
    help = 'Crear permisos iniciales del sistema Roy Representaciones'

    def handle(self, *args, **options):
        self.stdout.write('Creando permisos del sistema...')
        
        permisos_data = [
            # PRODUCTOS
            ('VER_PRODUCTOS', 'PRODUCTOS', 'VER', 'Ver listado de productos'),
            ('CREAR_PRODUCTOS', 'PRODUCTOS', 'CREAR', 'Crear nuevos productos'),
            ('EDITAR_PRODUCTOS', 'PRODUCTOS', 'EDITAR', 'Editar productos existentes'),
            ('ELIMINAR_PRODUCTOS', 'PRODUCTOS', 'ELIMINAR', 'Eliminar productos'),
            
            # INVENTARIO
            ('VER_INVENTARIO', 'INVENTARIO', 'VER', 'Ver inventario'),
            ('EDITAR_INVENTARIO', 'INVENTARIO', 'EDITAR', 'Ajustar inventario'),
            ('EXPORTAR_INVENTARIO', 'INVENTARIO', 'EXPORTAR', 'Exportar reportes de inventario'),
            
            # VENTAS
            ('VER_VENTAS', 'VENTAS', 'VER', 'Ver historial de ventas'),
            ('CREAR_VENTAS', 'VENTAS', 'CREAR', 'Realizar ventas'),
            ('ELIMINAR_VENTAS', 'VENTAS', 'ELIMINAR', 'Anular ventas'),
            
            # TRANSFERENCIAS
            ('VER_TRANSFERENCIAS', 'TRANSFERENCIAS', 'VER', 'Ver transferencias'),
            ('CREAR_TRANSFERENCIAS', 'TRANSFERENCIAS', 'CREAR', 'Crear transferencias'),
            ('EDITAR_TRANSFERENCIAS', 'TRANSFERENCIAS', 'EDITAR', 'Modificar transferencias'),
            
            # CLIENTES
            ('VER_CLIENTES', 'CLIENTES', 'VER', 'Ver clientes'),
            ('CREAR_CLIENTES', 'CLIENTES', 'CREAR', 'Registrar clientes'),
            ('EDITAR_CLIENTES', 'CLIENTES', 'EDITAR', 'Editar clientes'),
            
            # REPORTES
            ('VER_REPORTES', 'REPORTES', 'VER', 'Ver reportes'),
            ('EXPORTAR_REPORTES', 'REPORTES', 'EXPORTAR', 'Exportar reportes'),
            
            # USUARIOS
            ('VER_USUARIOS', 'USUARIOS', 'VER', 'Ver usuarios'),
            ('CREAR_USUARIOS', 'USUARIOS', 'CREAR', 'Crear usuarios'),
            ('EDITAR_USUARIOS', 'USUARIOS', 'EDITAR', 'Editar usuarios'),
            ('ELIMINAR_USUARIOS', 'USUARIOS', 'ELIMINAR', 'Eliminar usuarios'),
            
            # CONFIGURACIÓN
            ('VER_CONFIGURACION', 'CONFIGURACION', 'VER', 'Ver configuración'),
            ('EDITAR_CONFIGURACION', 'CONFIGURACION', 'EDITAR', 'Modificar configuración'),
        ]
        
        permisos_creados = 0
        for codigo, modulo, tipo, descripcion in permisos_data:
            permiso, created = Permiso.objects.get_or_create(
                codigo_permiso=codigo,
                defaults={
                    'nombre_permiso': descripcion,
                    'modulo': modulo,
                    'tipo_permiso': tipo,
                    'descripcion': descripcion
                }
            )
            if created:
                permisos_creados += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Creado: {codigo}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal permisos creados: {permisos_creados}'))
        
        # Asignar permisos a roles
        self.stdout.write('\nAsignando permisos a roles...')
        self.asignar_permisos_administrador()
        self.asignar_permisos_vendedores()
        
    def asignar_permisos_administrador(self):
        """Administrador tiene TODOS los permisos"""
        try:
            admin_rol = Rol.objects.get(nombre_rol='ADMINISTRADOR')
            todos_permisos = Permiso.objects.all()
            
            for permiso in todos_permisos:
                RolPermiso.objects.get_or_create(
                    rol=admin_rol,
                    permiso=permiso
                )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Administrador: {todos_permisos.count()} permisos'))
        except Rol.DoesNotExist:
            self.stdout.write(self.style.WARNING('Rol ADMINISTRADOR no existe'))
    
    def asignar_permisos_vendedores(self):
        """Vendedores tienen permisos limitados"""
        permisos_vendedor = [
            'VER_PRODUCTOS', 'VER_INVENTARIO', 'VER_VENTAS', 'CREAR_VENTAS',
            'VER_CLIENTES', 'CREAR_CLIENTES', 'EDITAR_CLIENTES',
            'VER_TRANSFERENCIAS', 'CREAR_TRANSFERENCIAS',
            'VER_REPORTES'
        ]
        
        for rol_nombre in ['VENDEDOR_ROYDENT', 'VENDEDOR_MUNDO_MEDICO']:
            try:
                rol = Rol.objects.get(nombre_rol=rol_nombre)
                contador = 0
                
                for codigo in permisos_vendedor:
                    try:
                        permiso = Permiso.objects.get(codigo_permiso=codigo)
                        RolPermiso.objects.get_or_create(
                            rol=rol,
                            permiso=permiso
                        )
                        contador += 1
                    except Permiso.DoesNotExist:
                        pass
                
                self.stdout.write(self.style.SUCCESS(f'✓ {rol_nombre}: {contador} permisos'))
            except Rol.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Rol {rol_nombre} no existe'))