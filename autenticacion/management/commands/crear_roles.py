"""
Management command para crear roles del sistema
"""
from django.core.management.base import BaseCommand
from autenticacion.models import Rol

class Command(BaseCommand):
    help = 'Crear roles predefinidos del sistema Roy Representaciones'

    def handle(self, *args, **options):
        self.stdout.write('Creando roles del sistema...')
        
        roles_data = [
            {
                'nombre_rol': 'ADMINISTRADOR',
                'descripcion': 'Administrador con acceso completo al sistema'
            },
            {
                'nombre_rol': 'VENDEDOR_ROYDENT',
                'descripcion': 'Vendedor de la sucursal RoyDent'
            },
            {
                'nombre_rol': 'VENDEDOR_MUNDO_MEDICO',
                'descripcion': 'Vendedor de la sucursal Mundo Médico'
            },
            {
                'nombre_rol': 'CLIENTE',
                'descripcion': 'Cliente con acceso limitado al catálogo'
            },
        ]
        
        roles_creados = 0
        for rol_data in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre_rol=rol_data['nombre_rol'],
                defaults={'descripcion': rol_data['descripcion']}
            )
            
            if created:
                roles_creados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creado: {rol_data["nombre_rol"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Ya existe: {rol_data["nombre_rol"]}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Total roles creados: {roles_creados}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ Total roles en BD: {Rol.objects.count()}')
        )