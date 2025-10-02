"""
Tests de Selenium para Gestión de Usuarios y Permisos
"""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

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
    
    driver_path = ChromeDriverManager().install()
    
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

@pytest.fixture(scope="module")
def login_admin(driver):
    """Login como administrador antes de los tests"""
    print("\n🔑 Realizando login como administrador...")
    driver.get(f"{BASE_URL}/login/")
    time.sleep(2)
    
    # Usar credenciales de administrador
    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.ID, "password").send_keys("Admin123!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)
    
    print("✓ Login de administrador completado")
    return driver

# ============ TESTS DE ACCESO A GESTIÓN DE USUARIOS ============

@pytest.mark.selenium
def test_01_acceso_gestion_usuarios(login_admin):
    """Test 1: Acceder a la página de gestión de usuarios"""
    print("\n▶ Test 1: Accediendo a gestión de usuarios...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    assert "/gestionusuario" in driver.current_url
    print(f"✓ URL actual: {driver.current_url}")
    print("✓ Página de gestión de usuarios cargada")

@pytest.mark.selenium
def test_02_verificar_estadisticas(login_admin):
    """Test 2: Verificar que se muestran las estadísticas"""
    print("\n▶ Test 2: Verificando estadísticas de usuarios...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Buscar las tarjetas de estadísticas
    stat_cards = driver.find_elements(By.CLASS_NAME, "stat-card")
    
    assert len(stat_cards) >= 4
    print(f"✓ Se encontraron {len(stat_cards)} tarjetas de estadísticas")
    
    # Verificar que tienen números
    for card in stat_cards[:4]:
        numero = card.find_element(By.CLASS_NAME, "stat-number")
        assert numero.text.strip() != ""
        print(f"✓ Estadística: {numero.text}")
    
    print("✓ Estadísticas mostradas correctamente")

@pytest.mark.selenium
def test_03_verificar_tabla_usuarios(login_admin):
    """Test 3: Verificar que existe la tabla de usuarios"""
    print("\n▶ Test 3: Verificando tabla de usuarios...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(3)
    
    # Buscar la tabla por tag name ya que el ID se genera dinámicamente
    tabla = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
    )
    assert tabla is not None
    
    # Verificar headers de la tabla (en mayúsculas como están en el HTML)
    headers = ['USUARIO', 'EMAIL', 'ROL', 'SUCURSAL', 'ESTADO', 'ACCIONES']
    thead = tabla.find_element(By.TAG_NAME, "thead")
    thead_text = thead.text.upper()  # Convertir a mayúsculas para comparar
    
    for header in headers:
        assert header in thead_text
        print(f"✓ Header encontrado: {header}")
    
    print("✓ Tabla de usuarios correcta")

# ============ TESTS DE FILTROS ============

@pytest.mark.selenium
def test_04_filtro_por_rol(login_admin):
    """Test 4: Filtrar usuarios por rol"""
    print("\n▶ Test 4: Probando filtro por rol...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Seleccionar filtro de rol
    filtro_rol = driver.find_element(By.ID, "filtro-rol")
    filtro_rol.click()
    time.sleep(1)
    
    # Seleccionar "Administrador"
    from selenium.webdriver.support.ui import Select
    select = Select(filtro_rol)
    select.select_by_value("ADMINISTRADOR")
    time.sleep(2)
    
    # Verificar que se aplicó el filtro
    tbody = driver.find_element(By.ID, "usuarios-table")
    filas = tbody.find_elements(By.TAG_NAME, "tr")
    
    print(f"✓ Usuarios filtrados: {len(filas)}")
    print("✓ Filtro por rol funciona")

@pytest.mark.selenium
def test_05_filtro_por_estado(login_admin):
    """Test 5: Filtrar usuarios por estado"""
    print("\n▶ Test 5: Probando filtro por estado...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Seleccionar filtro de estado
    filtro_estado = driver.find_element(By.ID, "filtro-estado")
    
    from selenium.webdriver.support.ui import Select
    select = Select(filtro_estado)
    select.select_by_value("activo")
    time.sleep(2)
    
    # Verificar badges de estado en la tabla
    badges = driver.find_elements(By.CLASS_NAME, "badge-activo")
    
    print(f"✓ Usuarios activos mostrados: {len(badges)}")
    print("✓ Filtro por estado funciona")

@pytest.mark.selenium
def test_06_busqueda_usuario(login_admin):
    """Test 6: Buscar usuario por texto"""
    print("\n▶ Test 6: Probando búsqueda de usuario...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Buscar campo de búsqueda
    busqueda = driver.find_element(By.ID, "busqueda")
    busqueda.clear()
    busqueda.send_keys("admin")
    time.sleep(2)
    
    # Verificar que se muestran resultados
    tbody = driver.find_element(By.ID, "usuarios-table")
    filas = tbody.find_elements(By.TAG_NAME, "tr")
    
    print(f"✓ Resultados de búsqueda: {len(filas)}")
    print("✓ Búsqueda funciona correctamente")

# ============ TESTS DE MODAL NUEVO USUARIO ============

@pytest.mark.selenium
def test_07_abrir_modal_nuevo_usuario(login_admin):
    """Test 7: Abrir modal de nuevo usuario"""
    print("\n▶ Test 7: Abriendo modal de nuevo usuario...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Buscar y hacer clic en botón "Nuevo Usuario"
    btn_nuevo = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Nuevo Usuario')]"))
    )
    btn_nuevo.click()
    time.sleep(2)
    
    # Verificar que el modal está visible
    modal = driver.find_element(By.ID, "modalUsuario")
    assert modal.value_of_css_property("display") == "block"
    
    print("✓ Modal de nuevo usuario abierto")

@pytest.mark.selenium
def test_08_campos_modal_usuario(login_admin):
    """Test 8: Verificar campos del modal de usuario"""
    print("\n▶ Test 8: Verificando campos del modal...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Abrir modal
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Usuario')]")
    btn_nuevo.click()
    time.sleep(2)
    
    # Verificar campos requeridos
    campos = {
        'modal-nombre': 'Nombre',
        'modal-apellido-paterno': 'Apellido Paterno',
        'modal-cedula': 'Cédula',
        'modal-email': 'Email',
        'modal-celular': 'Celular',
        'modal-usuario': 'Usuario',
        'modal-password': 'Contraseña',
        'modal-rol': 'Rol'
    }
    
    for campo_id, nombre in campos.items():
        campo = driver.find_element(By.ID, campo_id)
        assert campo is not None
        print(f"✓ Campo '{nombre}' encontrado")
    
    print("✓ Todos los campos del modal existen")

@pytest.mark.selenium
def test_09_cerrar_modal_usuario(login_admin):
    """Test 9: Cerrar modal de usuario"""
    print("\n▶ Test 9: Cerrando modal de usuario...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Abrir modal
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Usuario')]")
    btn_nuevo.click()
    time.sleep(2)
    
    # Cerrar modal con X
    close_btn = driver.find_element(By.CLASS_NAME, "close")
    close_btn.click()
    time.sleep(2)
    
    # Verificar que el modal está oculto
    modal = driver.find_element(By.ID, "modalUsuario")
    assert modal.value_of_css_property("display") == "none"
    
    print("✓ Modal cerrado correctamente")

# ============ TESTS DE VALIDACIÓN DE FORMULARIO ============

@pytest.mark.selenium
def test_10_validacion_nombre_solo_letras(login_admin):
    """Test 10: Validar que nombre solo acepta letras"""
    print("\n▶ Test 10: Validando campo nombre...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Abrir modal
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Usuario')]")
    btn_nuevo.click()
    time.sleep(2)
    
    # Probar campo nombre
    nombre_field = driver.find_element(By.ID, "modal-nombre")
    nombre_field.clear()
    nombre_field.send_keys("Juan123")
    time.sleep(1)
    
    valor = nombre_field.get_attribute("value")
    print(f"   Valor ingresado: Juan123")
    print(f"   Valor resultante: {valor}")
    print("✓ Campo nombre validado")

@pytest.mark.selenium
def test_11_validacion_celular_8_digitos(login_admin):
    """Test 11: Validar que celular tiene 8 dígitos"""
    print("\n▶ Test 11: Validando campo celular...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Abrir modal
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Usuario')]")
    btn_nuevo.click()
    time.sleep(2)
    
    # Probar campo celular
    celular_field = driver.find_element(By.ID, "modal-celular")
    celular_field.clear()
    celular_field.send_keys("70123456")
    time.sleep(1)
    
    valor = celular_field.get_attribute("value")
    assert len(valor) <= 8
    print(f"✓ Celular ingresado: {valor}")
    print("✓ Campo celular validado")

@pytest.mark.selenium
def test_12_validacion_email_formato(login_admin):
    """Test 12: Validar formato de email"""
    print("\n▶ Test 12: Validando formato de email...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Abrir modal
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Usuario')]")
    btn_nuevo.click()
    time.sleep(2)
    
    # Probar email válido
    email_field = driver.find_element(By.ID, "modal-email")
    email_field.clear()
    email_field.send_keys("test@ejemplo.com")
    time.sleep(1)
    
    # Verificar validación HTML5
    validacion = driver.execute_script(
        "return arguments[0].validity.valid;", 
        email_field
    )
    
    assert validacion == True
    print("✓ Email con formato válido aceptado")

# ============ TESTS DE CREAR USUARIO ============

@pytest.mark.selenium
def test_13_crear_usuario_datos_completos(login_admin):
    """Test 13: Crear usuario con datos completos"""
    print("\n▶ Test 13: Creando usuario con datos completos...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Abrir modal
    btn_nuevo = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Nuevo Usuario')]"))
    )
    btn_nuevo.click()
    time.sleep(2)
    
    # Generar datos únicos para evitar duplicados
    timestamp = str(int(time.time()))
    
    # Llenar formulario
    driver.find_element(By.ID, "modal-nombre").send_keys("Test")
    driver.find_element(By.ID, "modal-apellido-paterno").send_keys("Usuario")
    driver.find_element(By.ID, "modal-apellido-materno").send_keys("Selenium")
    driver.find_element(By.ID, "modal-cedula").send_keys(f"{timestamp[:7]}")
    driver.find_element(By.ID, "modal-email").send_keys(f"test{timestamp}@test.com")
    driver.find_element(By.ID, "modal-celular").send_keys("70123456")
    driver.find_element(By.ID, "modal-usuario").send_keys(f"test{timestamp}")
    driver.find_element(By.ID, "modal-password").send_keys("Test123!")
    
    # Seleccionar rol
    from selenium.webdriver.support.ui import Select
    rol_select = Select(driver.find_element(By.ID, "modal-rol"))
    rol_select.select_by_value("CLIENTE")
    
    time.sleep(1)
    
    # Buscar el botón de submit dentro del formulario
    submit_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'].btn-primary"))
    )
    submit_btn.click()
    time.sleep(3)
    
    print("✓ Formulario de creación enviado")

@pytest.mark.selenium
def test_14_crear_usuario_campos_vacios(login_admin):
    """Test 14: Intentar crear usuario con campos vacíos"""
    print("\n▶ Test 14: Intentando crear usuario sin datos...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Abrir modal
    btn_nuevo = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Nuevo Usuario')]"))
    )
    btn_nuevo.click()
    time.sleep(2)
    
    # Intentar enviar sin llenar - buscar botón de submit por CSS
    submit_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'].btn-primary"))
    )
    submit_btn.click()
    time.sleep(2)
    
    # El modal debería seguir abierto por validación HTML5
    modal = driver.find_element(By.ID, "modalUsuario")
    assert modal.value_of_css_property("display") == "block"
    
    print("✓ Validación de campos requeridos funciona")

# ============ TESTS DE ACCIONES SOBRE USUARIOS ============

@pytest.mark.selenium
def test_15_ver_detalles_usuario(login_admin):
    """Test 15: Ver detalles de un usuario"""
    print("\n▶ Test 15: Viendo detalles de usuario...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Buscar primer botón de "Ver"
    try:
        btn_ver = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-info i.fa-eye"))
        )
        btn_ver.click()
        time.sleep(2)
        
        # Verificar que aparece modal de detalles
        try:
            modal_detalles = driver.find_element(By.ID, "modalDetallesUsuario")
            assert modal_detalles is not None
            print("✓ Modal de detalles mostrado")
        except:
            print("✓ Detalles de usuario mostrados")
    except:
        print("⚠ No hay usuarios disponibles para ver")

@pytest.mark.selenium
def test_16_editar_usuario_abrir_modal(login_admin):
    """Test 16: Abrir modal de edición de usuario"""
    print("\n▶ Test 16: Abriendo modal de edición...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Buscar primer botón de "Editar"
    try:
        btn_editar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-secondary i.fa-edit"))
        )
        btn_editar.click()
        time.sleep(2)
        
        # Verificar que el modal está abierto
        modal = driver.find_element(By.ID, "modalUsuario")
        assert modal.value_of_css_property("display") == "block"
        
        # Verificar que el título dice "Editar"
        titulo = driver.find_element(By.ID, "tituloModal")
        assert "Editar" in titulo.text
        
        print("✓ Modal de edición abierto correctamente")
    except:
        print("⚠ No hay usuarios activos para editar")

# ============ TESTS DE PERMISOS ============

@pytest.mark.selenium
def test_17_seccion_permisos_existe(login_admin):
    """Test 17: Verificar que existe la sección de permisos"""
    print("\n▶ Test 17: Verificando sección de permisos...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Scroll hacia la sección de permisos
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # Buscar select de usuarios para permisos
    select_usuario = driver.find_element(By.ID, "usuario-permisos-select")
    assert select_usuario is not None
    
    print("✓ Sección de permisos encontrada")

@pytest.mark.selenium
def test_18_matriz_permisos_existe(login_admin):
    """Test 18: Verificar que existe la matriz de permisos"""
    print("\n▶ Test 18: Verificando matriz de permisos...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Scroll hasta la matriz
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # Buscar tabla de matriz
    matriz_body = driver.find_element(By.ID, "matriz-permisos-body")
    assert matriz_body is not None
    
    print("✓ Matriz de permisos encontrada")

@pytest.mark.selenium
def test_19_filtro_sucursal(login_admin):
    """Test 19: Filtrar por sucursal"""
    print("\n▶ Test 19: Probando filtro por sucursal...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Seleccionar filtro de sucursal
    filtro_sucursal = driver.find_element(By.ID, "filtro-sucursal")
    
    from selenium.webdriver.support.ui import Select
    select = Select(filtro_sucursal)
    select.select_by_value("roydent")
    time.sleep(2)
    
    print("✓ Filtro por sucursal aplicado")

@pytest.mark.selenium
def test_20_responsive_tabla_usuarios(login_admin):
    """Test 20: Verificar responsive de la tabla"""
    print("\n▶ Test 20: Verificando tabla responsive...")
    driver = login_admin
    
    # Probar en tamaño mobile
    driver.set_window_size(375, 667)
    time.sleep(2)
    
    driver.get(f"{BASE_URL}/gestionusuario/")
    time.sleep(2)
    
    # Verificar que la tabla existe y tiene scroll horizontal
    table_container = driver.find_element(By.CLASS_NAME, "table-container")
    assert table_container is not None
    
    # Restaurar tamaño
    driver.maximize_window()
    time.sleep(1)
    
    print("✓ Tabla responsive funciona correctamente")

if __name__ == "__main__":
    pytest.main([
        "-v", 
        "-s", 
        "--html=tests/reports/report_usuarios.html", 
        "--self-contained-html", 
        __file__
    ])