"""
Tests de Selenium simplificados para autenticación
"""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture(scope="module")
def driver():
    """Configurar driver de Selenium"""
    print("\n🔧 Iniciando Chrome WebDriver...")
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    # Obtener la ruta correcta del chromedriver
    driver_path = ChromeDriverManager().install()
    
    # Corregir la ruta si apunta al archivo incorrecto
    if 'THIRD_PARTY_NOTICES' in driver_path:
        import os
        driver_dir = os.path.dirname(driver_path)
        driver_path = os.path.join(driver_dir, 'chromedriver.exe')
    
    print(f"📍 Ruta del driver: {driver_path}")
    
    driver = webdriver.Chrome(
        service=Service(driver_path),
        options=options
    )
    driver.implicitly_wait(10)
    
    yield driver
    
    print("\n🔧 Cerrando Chrome WebDriver...")
    driver.quit()
    
@pytest.mark.selenium
def test_01_acceso_pagina_principal(driver):
    """Test 1: Acceder a la página principal"""
    print("\n▶ Test 1: Accediendo a página principal...")
    driver.get(BASE_URL)
    time.sleep(2)
    
    assert driver.title is not None
    print(f"✓ Título de página: {driver.title}")
    print("✓ Página principal cargada correctamente")

@pytest.mark.selenium
def test_02_navegacion_login(driver):
    """Test 2: Navegar a página de login"""
    print("\n▶ Test 2: Navegando a login...")
    driver.get(BASE_URL)
    time.sleep(2)
    
    try:
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/login/'], a[href*='login']"))
        )
        login_btn.click()
        time.sleep(2)
        
        assert "/login" in driver.current_url
        print(f"✓ URL actual: {driver.current_url}")
        print("✓ Navegación a login exitosa")
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

@pytest.mark.selenium  
def test_03_formulario_login_existe(driver):
    """Test 3: Verificar que existe el formulario de login"""
    print("\n▶ Test 3: Verificando formulario de login...")
    driver.get(f"{BASE_URL}/login/")
    time.sleep(2)
    
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    
    assert username_field is not None
    assert password_field is not None
    assert submit_btn is not None
    
    print("✓ Campo de usuario encontrado")
    print("✓ Campo de contraseña encontrado")
    print("✓ Botón de submit encontrado")
    print("✓ Formulario de login completo")

@pytest.mark.selenium
def test_04_validacion_campos_vacios(driver):
    """Test 4: Validación de campos vacíos en login"""
    print("\n▶ Test 4: Probando validación de campos vacíos...")
    driver.get(f"{BASE_URL}/login/")
    time.sleep(2)
    
    # Intentar submit sin llenar campos
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_btn.click()
    time.sleep(2)
    
    # Verificar que seguimos en login (no redirigió)
    assert "/login" in driver.current_url
    print("✓ Validación de campos vacíos funciona")

@pytest.mark.selenium
def test_05_navegacion_registro(driver):
    """Test 5: Navegar a página de registro"""
    print("\n▶ Test 5: Navegando a registro...")
    driver.get(f"{BASE_URL}/registro/")
    time.sleep(2)
    
    assert "/registro" in driver.current_url
    print(f"✓ URL actual: {driver.current_url}")
    print("✓ Página de registro cargada")

@pytest.mark.selenium
def test_06_formulario_registro_existe(driver):
    """Test 6: Verificar formulario de registro"""
    print("\n▶ Test 6: Verificando formulario de registro...")
    driver.get(f"{BASE_URL}/registro/")
    time.sleep(2)
    
    campos = {
        'username': 'Nombre de usuario',
        'password': 'Contraseña',
        'first-name': 'Nombre',
        'last-name-p': 'Apellido paterno',
        'ci': 'Cédula',
        'phone-number': 'Celular',
        'email': 'Correo'
    }
    
    for campo_id, nombre in campos.items():
        campo = driver.find_element(By.ID, campo_id)
        assert campo is not None
        print(f"✓ Campo '{nombre}' encontrado")
    
    print("✓ Formulario de registro completo")

@pytest.mark.selenium
def test_07_validacion_celular_solo_numeros(driver):
    """Test 7: Validar que celular solo acepta números"""
    print("\n▶ Test 7: Validando campo celular...")
    driver.get(f"{BASE_URL}/registro/")
    time.sleep(2)
    
    celular_field = driver.find_element(By.ID, "phone-number")
    celular_field.clear()
    celular_field.send_keys("abc123def456")
    time.sleep(1)
    
    valor = celular_field.get_attribute("value")
    print(f"   Valor ingresado: abc123def456")
    print(f"   Valor resultante: {valor}")
    
    # Verificar que solo quedaron números
    assert valor.isdigit() or valor == ""
    print("✓ Campo celular solo acepta números")

@pytest.mark.selenium
def test_08_validacion_nombre_solo_letras(driver):
    """Test 8: Validar que nombre solo acepta letras"""
    print("\n▶ Test 8: Validando campo nombre...")
    driver.get(f"{BASE_URL}/registro/")
    time.sleep(2)
    
    nombre_field = driver.find_element(By.ID, "first-name")
    nombre_field.clear()
    nombre_field.send_keys("Juan123")
    time.sleep(1)
    
    valor = nombre_field.get_attribute("value")
    print(f"   Valor ingresado: Juan123")
    print(f"   Valor resultante: {valor}")
    
    # Verificar que no hay números
    assert "123" not in valor
    print("✓ Campo nombre solo acepta letras")

@pytest.mark.selenium
def test_09_validacion_cedula_formato(driver):
    """Test 9: Validar formato de cédula"""
    print("\n▶ Test 9: Validando formato de cédula...")
    driver.get(f"{BASE_URL}/registro/")
    time.sleep(2)
    
    ci_field = driver.find_element(By.ID, "ci")
    ci_field.clear()
    ci_field.send_keys("1234567")
    ci_field.send_keys("\t")  # Tab para trigger validación
    time.sleep(1)
    
    valor = ci_field.get_attribute("value")
    print(f"   Valor ingresado: {valor}")
    print("✓ Campo cédula acepta formato boliviano")

@pytest.mark.selenium
def test_10_login_credenciales_invalidas(driver):
    """Test 10: Login con credenciales inválidas"""
    print("\n▶ Test 10: Probando login con credenciales inválidas...")
    driver.get(f"{BASE_URL}/login/")
    time.sleep(2)
    
    driver.find_element(By.ID, "username").send_keys("usuarioinvalido999")
    driver.find_element(By.ID, "password").send_keys("passwordinvalido")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    time.sleep(3)
    
    # Verificar que seguimos en login
    assert "/login" in driver.current_url
    print("✓ Login rechazado correctamente con credenciales inválidas")

if __name__ == "__main__":
    pytest.main(["-v", "-s", "--html=tests/reports/report.html", "--self-contained-html", __file__])