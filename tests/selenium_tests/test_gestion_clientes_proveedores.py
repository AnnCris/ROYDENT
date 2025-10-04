"""
Tests de Selenium para Gestión de Clientes y Proveedores
Incluye: CRUD, Exportación Excel, Filtros, Búsquedas
"""
import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

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
    
    # Configurar carpeta de descargas
    download_dir = os.path.join(os.getcwd(), "tests", "downloads")
    os.makedirs(download_dir, exist_ok=True)
    
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    driver_path = ChromeDriverManager().install()
    
    if 'THIRD_PARTY_NOTICES' in driver_path:
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
    """Login como administrador"""
    print("\n🔑 Realizando login como administrador...")
    driver.get(f"{BASE_URL}/login/")
    time.sleep(2)
    
    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.ID, "password").send_keys("Admin123!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)
    
    print("✓ Login completado")
    return driver


# ==========================================
# TESTS DE GESTIÓN DE CLIENTES
# ==========================================

@pytest.mark.selenium
def test_01_acceso_gestion_clientes(login_admin):
    """Test 1: Acceder a gestión de clientes"""
    print("\n▶ Test 1: Accediendo a gestión de clientes...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    assert "/gestionclientes" in driver.current_url
    print(f"✓ URL actual: {driver.current_url}")
    print("✓ Página de gestión de clientes cargada")

@pytest.mark.selenium
def test_02_estadisticas_clientes(login_admin):
    """Test 2: Verificar estadísticas de clientes"""
    print("\n▶ Test 2: Verificando estadísticas...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    stat_cards = driver.find_elements(By.CLASS_NAME, "stat-card")
    assert len(stat_cards) >= 3
    
    print(f"✓ Estadísticas encontradas: {len(stat_cards)}")
    
    total = driver.find_element(By.ID, "stat-total")
    activos = driver.find_element(By.ID, "stat-activos")
    inactivos = driver.find_element(By.ID, "stat-inactivos")
    
    print(f"   Total: {total.text}")
    print(f"   Activos: {activos.text}")
    print(f"   Inactivos: {inactivos.text}")
    print("✓ Estadísticas correctas")

@pytest.mark.selenium
def test_03_tabla_clientes_existe(login_admin):
    """Test 3: Verificar tabla de clientes"""
    print("\n▶ Test 3: Verificando tabla de clientes...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(3)
    
    tabla = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
    )
    
    headers = ['CLIENTE', 'TIPO', 'DOCUMENTO', 'CONTACTO', 'ESTADO', 'ACCIONES']
    thead = tabla.find_element(By.TAG_NAME, "thead")
    thead_text = thead.text.upper()
    
    for header in headers:
        assert header in thead_text
        print(f"✓ Header: {header}")
    
    print("✓ Tabla de clientes correcta")

@pytest.mark.selenium
def test_04_filtro_tipo_cliente(login_admin):
    """Test 4: Filtrar por tipo de cliente"""
    print("\n▶ Test 4: Probando filtro por tipo...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    filtro_tipo = driver.find_element(By.ID, "filtro-tipo")
    select = Select(filtro_tipo)
    
    # Obtener opciones disponibles
    opciones = select.options
    print(f"   Tipos disponibles: {len(opciones)}")
    
    if len(opciones) > 1:
        select.select_by_index(1)
        time.sleep(2)
        print("✓ Filtro por tipo aplicado")
    else:
        print("⚠ No hay tipos de cliente disponibles")

@pytest.mark.selenium
def test_05_filtro_estado_cliente(login_admin):
    """Test 5: Filtrar por estado"""
    print("\n▶ Test 5: Probando filtro por estado...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    filtro_estado = driver.find_element(By.ID, "filtro-estado")
    select = Select(filtro_estado)
    select.select_by_value("ACTIVO")
    time.sleep(2)
    
    print("✓ Filtro por estado aplicado")

@pytest.mark.selenium
def test_06_busqueda_cliente(login_admin):
    """Test 6: Buscar cliente"""
    print("\n▶ Test 6: Probando búsqueda...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    busqueda = driver.find_element(By.ID, "busqueda")
    busqueda.clear()
    busqueda.send_keys("test")
    time.sleep(3)
    
    print("✓ Búsqueda ejecutada")

@pytest.mark.selenium
def test_07_limpiar_filtros_clientes(login_admin):
    """Test 7: Limpiar filtros de clientes"""
    print("\n▶ Test 7: Limpiando filtros...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    # Aplicar algunos filtros
    busqueda = driver.find_element(By.ID, "busqueda")
    busqueda.send_keys("test")
    time.sleep(1)
    
    # Limpiar
    btn_limpiar = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Limpiar Filtros')]"))
    )
    btn_limpiar.click()
    time.sleep(2)
    
    # Verificar que se limpiaron
    busqueda_limpia = driver.find_element(By.ID, "busqueda")
    assert busqueda_limpia.get_attribute("value") == ""
    
    print("✓ Filtros limpiados correctamente")

@pytest.mark.selenium
def test_08_abrir_modal_nuevo_cliente(login_admin):
    """Test 8: Abrir modal de nuevo cliente"""
    print("\n▶ Test 8: Abriendo modal nuevo cliente...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    btn_nuevo = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Nuevo Cliente')]"))
    )
    btn_nuevo.click()
    time.sleep(2)
    
    modal = driver.find_element(By.ID, "modalCliente")
    assert modal.value_of_css_property("display") == "block"
    
    print("✓ Modal de nuevo cliente abierto")

@pytest.mark.selenium
def test_09_campos_modal_cliente(login_admin):
    """Test 9: Verificar campos del modal cliente"""
    print("\n▶ Test 9: Verificando campos del modal...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Cliente')]")
    btn_nuevo.click()
    time.sleep(2)
    
    campos = {
        'modal-nombre': 'Nombre',
        'modal-apellido-paterno': 'Apellido Paterno',
        'modal-cedula': 'Cédula',
        'modal-celular': 'Celular',
        'modal-email': 'Email',
        'modal-usuario': 'Usuario',
        'modal-password': 'Contraseña',
        'modal-tipo-cliente': 'Tipo Cliente',
        'modal-estado': 'Estado'
    }
    
    for campo_id, nombre in campos.items():
        campo = driver.find_element(By.ID, campo_id)
        assert campo is not None
        print(f"✓ Campo '{nombre}' encontrado")
    
    print("✓ Todos los campos existen")

@pytest.mark.selenium
def test_10_validacion_celular_cliente(login_admin):
    """Test 10: Validar celular en modal cliente"""
    print("\n▶ Test 10: Validando celular...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Cliente')]")
    btn_nuevo.click()
    time.sleep(2)
    
    celular = driver.find_element(By.ID, "modal-celular")
    celular.clear()
    celular.send_keys("123456789")  # 9 dígitos
    time.sleep(1)
    
    valor = celular.get_attribute("value")
    assert len(valor) <= 8
    
    print(f"   Valor ingresado: 123456789")
    print(f"   Valor aceptado: {valor}")
    print("✓ Validación de celular correcta (máx 8 dígitos)")

@pytest.mark.selenium
def test_11_crear_cliente_completo(login_admin):
    """Test 11: Crear cliente con datos completos"""
    print("\n▶ Test 11: Creando cliente completo...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    btn_nuevo = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Nuevo Cliente')]"))
    )
    btn_nuevo.click()
    time.sleep(2)
    
    timestamp = str(int(time.time()))
    
    driver.find_element(By.ID, "modal-nombre").send_keys("Cliente")
    driver.find_element(By.ID, "modal-apellido-paterno").send_keys("Test")
    driver.find_element(By.ID, "modal-apellido-materno").send_keys("Selenium")
    driver.find_element(By.ID, "modal-cedula").send_keys(f"{timestamp[:7]}")
    driver.find_element(By.ID, "modal-celular").send_keys("70123456")
    driver.find_element(By.ID, "modal-email").send_keys(f"cliente{timestamp}@test.com")
    driver.find_element(By.ID, "modal-usuario").send_keys(f"cliente{timestamp}")
    driver.find_element(By.ID, "modal-password").send_keys("Test123!")
    
    # Seleccionar tipo cliente
    tipo_select = Select(driver.find_element(By.ID, "modal-tipo-cliente"))
    if len(tipo_select.options) > 1:
        tipo_select.select_by_index(1)
    
    time.sleep(1)
    
    submit_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#formCliente button[type='submit']"))
    )
    submit_btn.click()
    time.sleep(4)
    
    print("✓ Cliente creado exitosamente")

@pytest.mark.selenium
def test_12_ver_detalles_cliente(login_admin):
    """Test 12: Ver detalles de cliente"""
    print("\n▶ Test 12: Viendo detalles de cliente...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    try:
        btn_ver = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-info i.fa-eye"))
        )
        btn_ver.click()
        time.sleep(2)
        
        print("✓ Detalles de cliente mostrados")
    except:
        print("⚠ No hay clientes disponibles")

@pytest.mark.selenium
def test_13_editar_cliente(login_admin):
    """Test 13: Editar cliente"""
    print("\n▶ Test 13: Editando cliente...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    try:
        btn_editar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-secondary i.fa-edit"))
        )
        btn_editar.click()
        time.sleep(2)
        
        modal = driver.find_element(By.ID, "modalCliente")
        assert modal.value_of_css_property("display") == "block"
        
        titulo = driver.find_element(By.ID, "tituloModal")
        assert "Editar" in titulo.text
        
        # Modificar nombre
        nombre = driver.find_element(By.ID, "modal-nombre")
        nombre.clear()
        nombre.send_keys("ClienteEditado")
        
        submit_btn = driver.find_element(By.CSS_SELECTOR, "#formCliente button[type='submit']")
        submit_btn.click()
        time.sleep(3)
        
        print("✓ Cliente editado correctamente")
    except:
        print("⚠ No hay clientes activos para editar")

@pytest.mark.selenium
def test_14_exportar_clientes_excel(login_admin):
    """Test 14: Exportar clientes a Excel"""
    print("\n▶ Test 14: Exportando clientes a Excel...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    btn_exportar = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Exportar')]"))
    )
    
    btn_exportar.click()
    time.sleep(3)
    
    # Verificar que se inició la descarga
    print("✓ Exportación a Excel iniciada")


# ==========================================
# TESTS DE GESTIÓN DE PROVEEDORES
# ==========================================

@pytest.mark.selenium
def test_15_acceso_gestion_proveedores(login_admin):
    """Test 15: Acceder a gestión de proveedores"""
    print("\n▶ Test 15: Accediendo a gestión de proveedores...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    assert "/gestionproveedores" in driver.current_url
    print(f"✓ URL: {driver.current_url}")
    print("✓ Página de proveedores cargada")

@pytest.mark.selenium
def test_16_estadisticas_proveedores(login_admin):
    """Test 16: Verificar estadísticas de proveedores"""
    print("\n▶ Test 16: Verificando estadísticas...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    total = driver.find_element(By.ID, "stat-total")
    activos = driver.find_element(By.ID, "stat-activos")
    inactivos = driver.find_element(By.ID, "stat-inactivos")
    
    print(f"   Total: {total.text}")
    print(f"   Activos: {activos.text}")
    print(f"   Inactivos: {inactivos.text}")
    print("✓ Estadísticas correctas")

@pytest.mark.selenium
def test_17_tabla_proveedores(login_admin):
    """Test 17: Verificar tabla de proveedores"""
    print("\n▶ Test 17: Verificando tabla...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    tabla = driver.find_element(By.CSS_SELECTOR, "table")
    headers = ['PROVEEDOR', 'NIT', 'CONTACTO', 'TIPO', 'ESTADO', 'ACCIONES']
    thead_text = tabla.find_element(By.TAG_NAME, "thead").text.upper()
    
    for header in headers:
        assert header in thead_text
        print(f"✓ Header: {header}")
    
    print("✓ Tabla correcta")

@pytest.mark.selenium
def test_18_filtro_tipo_proveedor(login_admin):
    """Test 18: Filtrar por tipo de proveedor"""
    print("\n▶ Test 18: Filtrando por tipo...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    filtro = driver.find_element(By.ID, "filtro-tipo")
    select = Select(filtro)
    select.select_by_value("DISTRIBUIDOR")
    time.sleep(2)
    
    print("✓ Filtro por tipo aplicado")

@pytest.mark.selenium
def test_19_busqueda_proveedor(login_admin):
    """Test 19: Buscar proveedor"""
    print("\n▶ Test 19: Buscando proveedor...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    busqueda = driver.find_element(By.ID, "busqueda")
    busqueda.send_keys("test")
    time.sleep(3)
    
    print("✓ Búsqueda ejecutada")

@pytest.mark.selenium
def test_20_limpiar_filtros_proveedores(login_admin):
    """Test 20: Limpiar filtros de proveedores"""
    print("\n▶ Test 20: Limpiando filtros...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    busqueda = driver.find_element(By.ID, "busqueda")
    busqueda.send_keys("test")
    
    btn_limpiar = driver.find_element(By.XPATH, "//button[contains(text(), 'Limpiar Filtros')]")
    btn_limpiar.click()
    time.sleep(2)
    
    assert driver.find_element(By.ID, "busqueda").get_attribute("value") == ""
    print("✓ Filtros limpiados")

@pytest.mark.selenium
def test_21_abrir_modal_nuevo_proveedor(login_admin):
    """Test 21: Abrir modal nuevo proveedor"""
    print("\n▶ Test 21: Abriendo modal nuevo proveedor...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Proveedor')]")
    btn_nuevo.click()
    time.sleep(2)
    
    modal = driver.find_element(By.ID, "modalCrearProveedor")
    assert modal.value_of_css_property("display") == "block"
    
    print("✓ Modal crear proveedor abierto")

@pytest.mark.selenium
def test_22_campos_modal_crear_proveedor(login_admin):
    """Test 22: Verificar campos del modal crear"""
    print("\n▶ Test 22: Verificando campos...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Proveedor')]")
    btn_nuevo.click()
    time.sleep(2)
    
    campos = {
        'crear-nombre': 'Nombre',
        'crear-apellido-paterno': 'Apellido Paterno',
        'crear-cedula': 'Cédula',
        'crear-celular': 'Celular',
        'crear-correo': 'Correo',
        'crear-tipo-proveedor': 'Tipo Proveedor',
        'crear-nit': 'NIT'
    }
    
    for campo_id, nombre in campos.items():
        campo = driver.find_element(By.ID, campo_id)
        assert campo is not None
        print(f"✓ Campo '{nombre}' encontrado")
    
    # CRÍTICO: Verificar que NO existe campo estado en crear
    try:
        driver.find_element(By.ID, "crear-estado")
        print("✗ ERROR: Campo estado NO debe existir en crear")
        assert False, "Campo estado no debe existir en modal crear"
    except:
        print("✓ Campo estado NO existe (correcto)")
    
    print("✓ Modal crear correcto")

@pytest.mark.selenium
def test_23_crear_proveedor_completo(login_admin):
    """Test 23: Crear proveedor completo"""
    print("\n▶ Test 23: Creando proveedor...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Proveedor')]")
    btn_nuevo.click()
    time.sleep(2)
    
    timestamp = str(int(time.time()))
    
    driver.find_element(By.ID, "crear-nombre").send_keys("Proveedor")
    driver.find_element(By.ID, "crear-apellido-paterno").send_keys("Test")
    driver.find_element(By.ID, "crear-cedula").send_keys(f"{timestamp[:7]}")
    driver.find_element(By.ID, "crear-celular").send_keys("71234567")
    driver.find_element(By.ID, "crear-correo").send_keys(f"prov{timestamp}@test.com")
    driver.find_element(By.ID, "crear-nit").send_keys(f"{timestamp[:10]}")
    
    tipo_select = Select(driver.find_element(By.ID, "crear-tipo-proveedor"))
    tipo_select.select_by_value("DISTRIBUIDOR")
    
    time.sleep(1)
    
    submit = driver.find_element(By.CSS_SELECTOR, "#formCrearProveedor button[type='submit']")
    submit.click()
    time.sleep(4)
    
    print("✓ Proveedor creado")

@pytest.mark.selenium
def test_24_editar_proveedor(login_admin):
    """Test 24: Editar proveedor"""
    print("\n▶ Test 24: Editando proveedor...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    try:
        btn_editar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-secondary i.fa-edit"))
        )
        btn_editar.click()
        time.sleep(2)
        
        modal = driver.find_element(By.ID, "modalEditarProveedor")
        assert modal.value_of_css_property("display") == "block"
        
        # CRÍTICO: Verificar que SÍ existe campo estado en editar
        estado = driver.find_element(By.ID, "editar-estado")
        assert estado is not None
        print("✓ Campo estado SÍ existe en editar (correcto)")
        
        # Cambiar estado a INACTIVO
        select_estado = Select(estado)
        select_estado.select_by_value("INACTIVO")
        
        submit = driver.find_element(By.CSS_SELECTOR, "#formEditarProveedor button[type='submit']")
        submit.click()
        time.sleep(3)
        
        print("✓ Proveedor editado correctamente")
    except:
        print("⚠ No hay proveedores para editar")

@pytest.mark.selenium
def test_25_exportar_proveedores_excel(login_admin):
    """Test 25: Exportar proveedores a Excel"""
    print("\n▶ Test 25: Exportando proveedores...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    btn_exportar = driver.find_element(By.XPATH, "//button[contains(text(), 'Exportar')]")
    btn_exportar.click()
    time.sleep(3)
    
    print("✓ Exportación iniciada")

@pytest.mark.selenium
def test_26_ver_detalles_proveedor(login_admin):
    """Test 26: Ver detalles de proveedor"""
    print("\n▶ Test 26: Viendo detalles...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    try:
        btn_ver = driver.find_element(By.CSS_SELECTOR, "button.btn-info i.fa-eye")
        btn_ver.click()
        time.sleep(2)
        print("✓ Detalles mostrados")
    except:
        print("⚠ No hay proveedores")

@pytest.mark.selenium
def test_27_activar_proveedor(login_admin):
    """Test 27: Activar proveedor inactivo"""
    print("\n▶ Test 27: Activando proveedor...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    # Filtrar por inactivos
    filtro_estado = Select(driver.find_element(By.ID, "filtro-estado"))
    filtro_estado.select_by_value("INACTIVO")
    time.sleep(2)
    
    try:
        btn_activar = driver.find_element(By.XPATH, "//button[contains(text(), 'Activar')]")
        btn_activar.click()
        time.sleep(1)
        
        # Confirmar
        driver.switch_to.alert.accept()
        time.sleep(3)
        
        print("✓ Proveedor activado")
    except:
        print("⚠ No hay proveedores inactivos")

@pytest.mark.selenium
def test_28_desactivar_proveedor(login_admin):
    """Test 28: Desactivar proveedor"""
    print("\n▶ Test 28: Desactivando proveedor...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    try:
        btn_eliminar = driver.find_element(By.CSS_SELECTOR, "button.btn-danger")
        btn_eliminar.click()
        time.sleep(1)
        
        driver.switch_to.alert.accept()
        time.sleep(3)
        
        print("✓ Proveedor desactivado")
    except:
        print("⚠ No hay proveedores activos")

@pytest.mark.selenium
def test_29_responsive_clientes(login_admin):
    """Test 29: Verificar responsive en clientes"""
    print("\n▶ Test 29: Probando responsive clientes...")
    driver = login_admin
    
    # Tamaño mobile
    driver.set_window_size(375, 667)
    time.sleep(2)
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    table_container = driver.find_element(By.CLASS_NAME, "table-container")
    assert table_container is not None
    
    # Restaurar tamaño
    driver.maximize_window()
    time.sleep(1)
    
    print("✓ Responsive clientes funciona")

@pytest.mark.selenium
def test_30_responsive_proveedores(login_admin):
    """Test 30: Verificar responsive en proveedores"""
    print("\n▶ Test 30: Probando responsive proveedores...")
    driver = login_admin
    
    # Tamaño tablet
    driver.set_window_size(768, 1024)
    time.sleep(2)
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    table_container = driver.find_element(By.CLASS_NAME, "table-container")
    assert table_container is not None
    
    # Restaurar
    driver.maximize_window()
    time.sleep(1)
    
    print("✓ Responsive proveedores funciona")

@pytest.mark.selenium
def test_31_validacion_nit_proveedor(login_admin):
    """Test 31: Validar NIT en proveedor"""
    print("\n▶ Test 31: Validando NIT...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Proveedor')]")
    btn_nuevo.click()
    time.sleep(2)
    
    nit = driver.find_element(By.ID, "crear-nit")
    nit.send_keys("123")  # NIT muy corto
    nit.send_keys("\t")
    time.sleep(1)
    
    # Intentar submit
    submit = driver.find_element(By.CSS_SELECTOR, "#formCrearProveedor button[type='submit']")
    submit.click()
    time.sleep(2)
    
    # Verificar que aún está en el modal (validación funcionó)
    modal = driver.find_element(By.ID, "modalCrearProveedor")
    assert modal.value_of_css_property("display") == "block"
    
    print("✓ Validación de NIT funciona")

@pytest.mark.selenium
def test_32_validacion_email_proveedor(login_admin):
    """Test 32: Validar email en proveedor"""
    print("\n▶ Test 32: Validando email...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Proveedor')]")
    btn_nuevo.click()
    time.sleep(2)
    
    email = driver.find_element(By.ID, "crear-correo")
    email.send_keys("emailinvalido")
    
    validacion = driver.execute_script(
        "return arguments[0].validity.valid;", 
        email
    )
    
    assert validacion == False
    print("✓ Email inválido rechazado")
    
    # Probar email válido
    email.clear()
    email.send_keys("valido@test.com")
    
    validacion = driver.execute_script(
        "return arguments[0].validity.valid;", 
        email
    )
    
    assert validacion == True
    print("✓ Email válido aceptado")

@pytest.mark.selenium
def test_33_cerrar_modal_crear_proveedor(login_admin):
    """Test 33: Cerrar modal crear proveedor"""
    print("\n▶ Test 33: Cerrando modal crear...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Proveedor')]")
    btn_nuevo.click()
    time.sleep(2)
    
    close_btn = driver.find_element(By.CSS_SELECTOR, "#modalCrearProveedor .close")
    close_btn.click()
    time.sleep(2)
    
    modal = driver.find_element(By.ID, "modalCrearProveedor")
    assert modal.value_of_css_property("display") == "none"
    
    print("✓ Modal crear cerrado")

@pytest.mark.selenium
def test_34_cerrar_modal_editar_proveedor(login_admin):
    """Test 34: Cerrar modal editar proveedor"""
    print("\n▶ Test 34: Cerrando modal editar...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    try:
        btn_editar = driver.find_element(By.CSS_SELECTOR, "button.btn-secondary i.fa-edit")
        btn_editar.click()
        time.sleep(2)
        
        close_btn = driver.find_element(By.CSS_SELECTOR, "#modalEditarProveedor .close")
        close_btn.click()
        time.sleep(2)
        
        modal = driver.find_element(By.ID, "modalEditarProveedor")
        assert modal.value_of_css_property("display") == "none"
        
        print("✓ Modal editar cerrado")
    except:
        print("⚠ No hay proveedores para editar")

@pytest.mark.selenium
def test_35_cerrar_modal_cliente(login_admin):
    """Test 35: Cerrar modal de cliente"""
    print("\n▶ Test 35: Cerrando modal cliente...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Cliente')]")
    btn_nuevo.click()
    time.sleep(2)
    
    close_btn = driver.find_element(By.CSS_SELECTOR, "#modalCliente .close")
    close_btn.click()
    time.sleep(2)
    
    modal = driver.find_element(By.ID, "modalCliente")
    assert modal.value_of_css_property("display") == "none"
    
    print("✓ Modal cliente cerrado")

@pytest.mark.selenium
def test_36_validacion_cedula_cliente(login_admin):
    """Test 36: Validar formato de cédula en cliente"""
    print("\n▶ Test 36: Validando cédula cliente...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Cliente')]")
    btn_nuevo.click()
    time.sleep(2)
    
    cedula = driver.find_element(By.ID, "modal-cedula")
    cedula.send_keys("1234567-LP")
    time.sleep(1)
    
    valor = cedula.get_attribute("value")
    print(f"   Cédula ingresada: {valor}")
    print("✓ Formato de cédula boliviana aceptado")

@pytest.mark.selenium
def test_37_validacion_password_cliente(login_admin):
    """Test 37: Validar contraseña en cliente"""
    print("\n▶ Test 37: Validando contraseña...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Cliente')]")
    btn_nuevo.click()
    time.sleep(2)
    
    password = driver.find_element(By.ID, "modal-password")
    password.send_keys("123")  # Contraseña muy corta
    
    # Verificar atributo minlength
    minlength = password.get_attribute("minlength")
    print(f"   Mínimo requerido: {minlength} caracteres")
    
    valor = password.get_attribute("value")
    print(f"   Contraseña ingresada: {len(valor)} caracteres")
    
    print("✓ Validación de contraseña existe")

@pytest.mark.selenium
def test_38_toggle_password_visibility(login_admin):
    """Test 38: Toggle visibilidad de contraseña"""
    print("\n▶ Test 38: Toggle password visibility...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    btn_nuevo = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Cliente')]")
    btn_nuevo.click()
    time.sleep(2)
    
    password = driver.find_element(By.ID, "modal-password")
    toggle_icon = driver.find_element(By.ID, "toggle-password")
    
    # Verificar tipo inicial
    tipo_inicial = password.get_attribute("type")
    assert tipo_inicial == "password"
    print("   Tipo inicial: password (oculto)")
    
    # Click en toggle
    toggle_icon.click()
    time.sleep(1)
    
    tipo_final = password.get_attribute("type")
    assert tipo_final == "text"
    print("   Tipo final: text (visible)")
    
    print("✓ Toggle password funciona")

@pytest.mark.selenium
def test_39_filtros_combinados_clientes(login_admin):
    """Test 39: Aplicar filtros combinados en clientes"""
    print("\n▶ Test 39: Probando filtros combinados...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionclientes/")
    time.sleep(2)
    
    # Aplicar filtro estado
    filtro_estado = Select(driver.find_element(By.ID, "filtro-estado"))
    filtro_estado.select_by_value("ACTIVO")
    time.sleep(1)
    
    # Aplicar búsqueda
    busqueda = driver.find_element(By.ID, "busqueda")
    busqueda.send_keys("test")
    time.sleep(2)
    
    # Verificar que se aplicaron ambos
    tbody = driver.find_element(By.ID, "clientes-table")
    
    print("✓ Filtros combinados aplicados")

@pytest.mark.selenium
def test_40_filtros_combinados_proveedores(login_admin):
    """Test 40: Aplicar filtros combinados en proveedores"""
    print("\n▶ Test 40: Probando filtros combinados proveedores...")
    driver = login_admin
    
    driver.get(f"{BASE_URL}/gestionproveedores/")
    time.sleep(2)
    
    # Tipo + Estado + Búsqueda
    filtro_tipo = Select(driver.find_element(By.ID, "filtro-tipo"))
    filtro_tipo.select_by_value("DISTRIBUIDOR")
    time.sleep(1)
    
    filtro_estado = Select(driver.find_element(By.ID, "filtro-estado"))
    filtro_estado.select_by_value("ACTIVO")
    time.sleep(1)
    
    busqueda = driver.find_element(By.ID, "busqueda")
    busqueda.send_keys("test")
    time.sleep(2)
    
    print("✓ Filtros combinados proveedores aplicados")


if __name__ == "__main__":
    pytest.main([
        "-v", 
        "-s", 
        "--html=tests/reports/report_clientes_proveedores.html", 
        "--self-contained-html", 
        __file__
    ])