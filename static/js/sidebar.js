// static/js/sidebar.js
// Sistema de Sidebar Responsive - RoyDent

(function() {
    'use strict';
    
    let sidebarInitialized = false;

    // ============ FUNCIONES PRINCIPALES ============
    
    function toggleSidebarDesktop() {
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.querySelector('.main-content');
        
        if (!sidebar) return;
        
        sidebar.classList.toggle('collapsed');
        if (mainContent) {
            mainContent.classList.toggle('sidebar-collapsed');
        }
        
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', isCollapsed);
    }

    function toggleSidebarMobile() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        
        if (!sidebar) return;
        
        sidebar.classList.toggle('active');
        if (overlay) {
            overlay.classList.toggle('active');
        }
        
        document.body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
    }

    function cerrarSidebarEnMovil() {
        if (window.innerWidth <= 1024) {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            
            if (sidebar) sidebar.classList.remove('active');
            if (overlay) overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    function marcarPaginaActiva() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            const href = link.getAttribute('href');
            
            if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
                link.classList.add('active');
            }
        });
    }

    function restaurarEstadoSidebar() {
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        
        if (isCollapsed && window.innerWidth > 1024) {
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.querySelector('.main-content');
            
            if (sidebar) sidebar.classList.add('collapsed');
            if (mainContent) mainContent.classList.add('sidebar-collapsed');
        }
    }

    function handleResize() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        const mainContent = document.querySelector('.main-content');
        
        if (window.innerWidth > 1024) {
            if (sidebar) sidebar.classList.remove('active');
            if (overlay) overlay.classList.remove('active');
            document.body.style.overflow = '';
            restaurarEstadoSidebar();
        } else {
            if (sidebar) sidebar.classList.remove('collapsed');
            if (mainContent) mainContent.classList.remove('sidebar-collapsed');
        }
    }

    function handleLogoError(e) {
        const img = e.target;
        const defaultLogo = document.getElementById('defaultLogo');
        
        if (img) img.style.display = 'none';
        if (defaultLogo) defaultLogo.style.display = 'flex';
    }

    function handleMobileLogoError(e) {
        const img = e.target;
        const mobileHeader = document.getElementById('mobile-header');
        
        if (img) img.style.display = 'none';
        
        if (mobileHeader && !mobileHeader.querySelector('.mobile-logo-text')) {
            const logoText = document.createElement('span');
            logoText.className = 'mobile-logo-text';
            logoText.textContent = 'Sistema Roy';
            logoText.style.cssText = `
                font-family: Inter, sans-serif;
                font-weight: 700;
                font-size: 1.2rem;
                color: var(--color-green-dark);
            `;
            mobileHeader.appendChild(logoText);
        }
    }

    // ============ INICIALIZAR EVENT LISTENERS ============
    
    function inicializarEventListeners() {
        if (sidebarInitialized) return;

        // Botón toggle desktop
        const toggleDesktopBtn = document.getElementById('sidebarToggleDesktop');
        if (toggleDesktopBtn) {
            toggleDesktopBtn.addEventListener('click', toggleSidebarDesktop);
        }

        // Botón toggle móvil
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        if (mobileMenuBtn) {
            mobileMenuBtn.addEventListener('click', toggleSidebarMobile);
        }

        // Overlay
        const overlay = document.getElementById('sidebar-overlay');
        if (overlay) {
            overlay.addEventListener('click', toggleSidebarMobile);
        }

        // Links del sidebar
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', cerrarSidebarEnMovil);
        });

        // Logos
        const sidebarLogo = document.getElementById('sidebarLogo');
        const mobileLogo = document.getElementById('mobileLogo');
        
        if (sidebarLogo) {
            sidebarLogo.addEventListener('error', handleLogoError);
            if (sidebarLogo.complete && sidebarLogo.naturalHeight === 0) {
                handleLogoError({ target: sidebarLogo });
            }
        }
        
        if (mobileLogo) {
            mobileLogo.addEventListener('error', handleMobileLogoError);
            if (mobileLogo.complete && mobileLogo.naturalHeight === 0) {
                handleMobileLogoError({ target: mobileLogo });
            }
        }

        // Tecla ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && window.innerWidth <= 1024) {
                const sidebar = document.getElementById('sidebar');
                if (sidebar && sidebar.classList.contains('active')) {
                    toggleSidebarMobile();
                }
            }
        });

        // Resize
        window.addEventListener('resize', handleResize);

        sidebarInitialized = true;
    }

    // ============ INICIALIZACIÓN PRINCIPAL ============
    
    function inicializarSidebar() {
        marcarPaginaActiva();
        restaurarEstadoSidebar();
        inicializarEventListeners();
    }

    // ============ EXPORTAR FUNCIÓN GLOBAL ============
    
    window.initSidebar = function() {
        // Resetear el flag para permitir reinicialización
        sidebarInitialized = false;
        inicializarSidebar();
    };

})();