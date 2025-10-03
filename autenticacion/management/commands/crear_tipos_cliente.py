# autenticacion/management/commands/crear_tipos_cliente.py

"""
Management command para crear tipos de cliente predefinidos
"""
from django.core.management.base import BaseCommand
from autenticacion.models import TipoCliente

class Command(BaseCommand):
    help = 'Crear tipos de cliente predefinidos del sistema'

    def handle(self, *args, **options):
        self.stdout.write('Creando tipos de cliente...')
        
        tipos_data = [
            ('ODONTOLOGO', 'Odontólogo', 'Profesional en odontología'),
            ('MEDICO', 'Médico', 'Profesional en medicina general o especializada'),
            ('EST_ODONTOLOGIA', 'Estudiante Odontología', 'Estudiante de la carrera de odontología'),
            ('EST_MEDICINA', 'Estudiante Medicina', 'Estudiante de la carrera de medicina'),
            ('EST_ENFERMERIA', 'Estudiante Enfermería', 'Estudiante de la carrera de enfermería'),
            ('EST_VETERINARIA', 'Estudiante Veterinaria', 'Estudiante de la carrera de veterinaria'),
            ('ENFERMERO', 'Enfermero/a', 'Profesional en enfermería'),
            ('VETERINARIO', 'Veterinario/a', 'Profesional en veterinaria'),
            ('LAB_DENTAL', 'Laboratorio Dental', 'Laboratorio técnico dental'),
        ]
        
        tipos_creados = 0
        for codigo, nombre, descripcion in tipos_data:
            tipo, created = TipoCliente.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre_tipo': nombre,
                    'descripcion': descripcion
                }
            )
            if created:
                tipos_creados += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Creado: {nombre}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠ Ya existe: {nombre}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal tipos creados: {tipos_creados}'))
        self.stdout.write(self.style.SUCCESS(f'Total tipos en BD: {TipoCliente.objects.count()}'))