# conftest.py en la raíz del proyecto
import pytest
import django
from django.conf import settings

def pytest_configure(config):
    """Configurar Django para tests"""
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
            ],
        )
        django.setup()

@pytest.fixture(scope='session')
def django_db_setup():
    """Override de configuración de base de datos"""
    pass

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Habilitar acceso a DB para todos los tests"""
    pass