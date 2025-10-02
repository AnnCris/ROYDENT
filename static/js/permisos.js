// static/js/permisos.js
// Sistema de Gestión de Permisos - RoyDent

(function() {
    'use strict';

    // ============ VARIABLES GLOBALES ============
    let todosLosPermisos = [];
    let permisosUsuarioActual = [];
    let usuarioSeleccionadoId = null;
    let rolesPermisos = {};

    // ============ ICONOS POR MÓDULO ============
    const iconosModulo = {
        'PRODUCTOS': '📦',
        'INVENTARIO': '📋',
        'VENTAS': '💰',
        'TRANSFERENCIAS': '🔄',
        'CLIENTES': '👥',
        'REPORTES': '📊',
        'USUARIOS': '👤',
        'CONFIGURACION': '⚙️'
    };

    // ============ ICONOS POR TIPO DE PERMISO ============
    const iconosTipoPermiso = {
        'VER': '👁️',
        'CREAR': '➕',
        'EDITAR': '✏️',
        'ELIMINAR': '🗑️',
        'EXPORTAR': '📤',
        'IMPORTAR': '📥'
    };

    // ============ CARGAR TODOS LOS PERMISOS ============
    async function cargarTodosLosPermisos() {
        try {
            const response = await fetch('/auth/api/permisos/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            if (!response.ok) throw new Error('Error al cargar permisos');

            const data = await response.json();
            
            if (data.success) {
                todosLosPermisos = data.permisos || [];
                await cargarMatrizPermisos();
            }
        } catch (error) {
            console.error('Error al cargar permisos:', error);
            mostrarAlerta('Error al cargar permisos del sistema', 'danger');
        }
    }

    // ============ CARGAR USUARIOS EN SELECT ============
    async function cargarUsuariosSelect() {
        try {
            const response = await fetch('/auth/api/usuarios/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            if (!response.ok) throw new Error('Error al cargar usuarios');

            const data = await response.json();
            
            if (data.success) {
                const select = document.getElementById('usuario-permisos-select');
                select.innerHTML = '<option value="">Selecciona un usuario...</option>';
                
                data.usuarios.forEach(usuario => {
                    if (usuario.is_active) {
                        const option = document.createElement('option');
                        option.value = usuario.id;
                        option.textContent = `${usuario.nombre_completo} (@${usuario.nombre_usuario})`;
                        option.dataset.rol = usuario.roles[0]?.nombre || 'Sin rol';
                        select.appendChild(option);
                    }
                });
            }
        } catch (error) {
            console.error('Error al cargar usuarios:', error);
        }
    }

    // ============ CARGAR PERMISOS DE UN USUARIO ============
    window.cargarPermisosUsuario = async function() {
        const select = document.getElementById('usuario-permisos-select');
        const usuarioId = select.value;
        
        if (!usuarioId) {
            document.getElementById('permisos-container').style.display = 'none';
            return;
        }

        usuarioSeleccionadoId = usuarioId;
        const selectedOption = select.options[select.selectedIndex];
        const rolUsuario = selectedOption.dataset.rol;

        try {
            const response = await fetch(`/auth/api/usuarios/${usuarioId}/permisos/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            if (!response.ok) throw new Error('Error al cargar permisos del usuario');

            const data = await response.json();
            
            if (data.success) {
                permisosUsuarioActual = data.permisos || [];
                
                // Actualizar información del usuario
                document.getElementById('usuario-seleccionado-nombre').textContent = selectedOption.textContent;
                document.getElementById('usuario-seleccionado-rol').textContent = rolUsuario;
                
                // Mostrar contenedor y renderizar permisos
                document.getElementById('permisos-container').style.display = 'block';
                renderizarPermisosUsuario();
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarAlerta('Error al cargar permisos del usuario', 'danger');
        }
    };

    // ============ RENDERIZAR PERMISOS DEL USUARIO ============
    function renderizarPermisosUsuario() {
        const grid = document.getElementById('permisos-grid');
        grid.innerHTML = '';

        // Agrupar permisos por módulo
        const permisosPorModulo = {};
        
        todosLosPermisos.forEach(permiso => {
            if (!permisosPorModulo[permiso.modulo]) {
                permisosPorModulo[permiso.modulo] = [];
            }
            permisosPorModulo[permiso.modulo].push(permiso);
        });

        // Crear card por cada módulo
        Object.keys(permisosPorModulo).sort().forEach(modulo => {
            const permisos = permisosPorModulo[modulo];
            const icono = iconosModulo[modulo] || '📌';
            
            const moduloDiv = document.createElement('div');
            moduloDiv.className = 'permiso-modulo';
            
            let html = `
                <h3>
                    <span>${icono}</span>
                    ${modulo}
                </h3>
                <div class="select-all-container" onclick="toggleTodosPermisos('${modulo}')">
                    <input type="checkbox" 
                           class="select-all-checkbox" 
                           id="select-all-${modulo}"
                           onclick="event.stopPropagation(); toggleTodosPermisos('${modulo}')">
                    <label for="select-all-${modulo}" style="cursor: pointer; user-select: none;">
                        Seleccionar todos
                    </label>
                </div>
            `;
            
            permisos.forEach(permiso => {
                const tienePermiso = permisosUsuarioActual.some(p => p.id === permiso.id);
                const iconoTipo = iconosTipoPermiso[permiso.tipo_permiso] || '•';
                
                html += `
                    <div class="permiso-item">
                        <label class="permiso-label">
                            <input type="checkbox" 
                                   class="permiso-checkbox permiso-${modulo}" 
                                   data-permiso-id="${permiso.id}"
                                   ${tienePermiso ? 'checked' : ''}
                                   onchange="verificarSelectAll('${modulo}')">
                            <span class="permiso-icon">${iconoTipo}</span>
                            <span>${permiso.nombre_permiso}</span>
                        </label>
                    </div>
                `;
            });
            
            moduloDiv.innerHTML = html;
            grid.appendChild(moduloDiv);
            
            // Verificar si todos están seleccionados
            verificarSelectAll(modulo);
        });
    }

    // ============ TOGGLE TODOS LOS PERMISOS DE UN MÓDULO ============
    window.toggleTodosPermisos = function(modulo) {
        const selectAllCheckbox = document.getElementById(`select-all-${modulo}`);
        const checkboxes = document.querySelectorAll(`.permiso-${modulo}`);
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAllCheckbox.checked;
        });
    };

    // ============ VERIFICAR SELECT ALL ============
    window.verificarSelectAll = function(modulo) {
        const checkboxes = document.querySelectorAll(`.permiso-${modulo}`);
        const selectAllCheckbox = document.getElementById(`select-all-${modulo}`);
        
        const todosSeleccionados = Array.from(checkboxes).every(cb => cb.checked);
        const algunoSeleccionado = Array.from(checkboxes).some(cb => cb.checked);
        
        selectAllCheckbox.checked = todosSeleccionados;
        selectAllCheckbox.indeterminate = algunoSeleccionado && !todosSeleccionados;
    };

    // ============ GUARDAR PERMISOS DEL USUARIO ============
    window.guardarPermisosUsuario = async function() {
        if (!usuarioSeleccionadoId) return;

        // Obtener todos los permisos seleccionados
        const checkboxes = document.querySelectorAll('.permiso-checkbox:checked');
        const permisosIds = Array.from(checkboxes).map(cb => parseInt(cb.dataset.permisoId));

        try {
            const response = await fetch(`/auth/api/usuarios/${usuarioSeleccionadoId}/permisos/actualizar/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include',
                body: JSON.stringify({
                    permisos: permisosIds
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                mostrarAlerta('Permisos actualizados exitosamente', 'success');
                await cargarMatrizPermisos(); // Actualizar matriz
            } else {
                throw new Error(data.error || 'Error al guardar permisos');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarAlerta('Error al guardar permisos: ' + error.message, 'danger');
        }
    };

    // ============ CANCELAR EDICIÓN ============
    window.cancelarEdicionPermisos = function() {
        document.getElementById('usuario-permisos-select').value = '';
        document.getElementById('permisos-container').style.display = 'none';
        usuarioSeleccionadoId = null;
        permisosUsuarioActual = [];
    };

    // ============ CARGAR MATRIZ DE PERMISOS ============
    async function cargarMatrizPermisos() {
        try {
            const response = await fetch('/auth/api/roles/permisos/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            if (!response.ok) throw new Error('Error al cargar matriz');

            const data = await response.json();
            
            if (data.success) {
                rolesPermisos = data.roles_permisos || {};
                renderizarMatrizPermisos();
            }
        } catch (error) {
            console.error('Error al cargar matriz:', error);
        }
    }

    // ============ RENDERIZAR MATRIZ DE PERMISOS ============
    function renderizarMatrizPermisos() {
        const tbody = document.getElementById('matriz-permisos-body');
        tbody.innerHTML = '';

        // Agrupar por módulo
        const permisosPorModulo = {};
        todosLosPermisos.forEach(permiso => {
            if (!permisosPorModulo[permiso.modulo]) {
                permisosPorModulo[permiso.modulo] = [];
            }
            permisosPorModulo[permiso.modulo].push(permiso);
        });

        // Roles a mostrar
        const roles = ['ADMINISTRADOR', 'VENDEDOR_ROYDENT', 'VENDEDOR_MUNDO_MEDICO', 'CLIENTE'];

        Object.keys(permisosPorModulo).sort().forEach(modulo => {
            const permisos = permisosPorModulo[modulo];
            const icono = iconosModulo[modulo] || '📌';
            
            permisos.forEach((permiso, index) => {
                const tr = document.createElement('tr');
                
                if (index === 0) {
                    const tdModulo = document.createElement('td');
                    tdModulo.rowSpan = permisos.length;
                    tdModulo.innerHTML = `<strong>${icono} ${modulo}</strong>`;
                    tdModulo.style.verticalAlign = 'top';
                    tdModulo.style.background = 'rgba(255, 215, 0, 0.1)';
                    tr.appendChild(tdModulo);
                }
                
                roles.forEach(rol => {
                    const td = document.createElement('td');
                    td.style.textAlign = 'center';
                    
                    const tienePermiso = rolesPermisos[rol]?.includes(permiso.id);
                    
                    td.innerHTML = tienePermiso 
                        ? '<i class="fas fa-check-circle matriz-permiso-activo"></i>' 
                        : '<i class="fas fa-times-circle matriz-permiso-inactivo"></i>';
                    
                    tr.appendChild(td);
                });
                
                tbody.appendChild(tr);
            });
        });
    }

    // ============ FUNCIÓN DE ALERTA ============
    function mostrarAlerta(mensaje, tipo) {
        // Reutilizar la función del archivo principal
        if (window.mostrarAlerta) {
            window.mostrarAlerta(mensaje, tipo);
        } else {
            alert(mensaje);
        }
    }

    // ============ INICIALIZACIÓN ============
    document.addEventListener('DOMContentLoaded', function() {
        cargarTodosLosPermisos();
        cargarUsuariosSelect();
    });

    // Exportar funciones necesarias
    window.permisosManager = {
        recargar: function() {
            cargarTodosLosPermisos();
            cargarUsuariosSelect();
        }
    };

})();