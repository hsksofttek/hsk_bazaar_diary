document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const toggle = document.getElementById('sidebarToggle');

    function closeDrawer() {
        if (sidebar) sidebar.classList.remove('show');
        if (overlay) overlay.classList.remove('active');
    }

    function openDrawer() {
        if (sidebar) sidebar.classList.add('show');
        if (overlay) overlay.classList.add('active');
    }

    if (toggle) {
        toggle.addEventListener('click', function(e) {
            if (window.innerWidth <= 992) {
                if (sidebar && sidebar.classList.contains('show')) {
                    closeDrawer();
                } else {
                    openDrawer();
                }
                e.stopPropagation();
            }
        });
    }

    if (overlay) {
        overlay.addEventListener('click', closeDrawer);
    }

    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 992 && sidebar && sidebar.classList.contains('show')) {
            if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
                closeDrawer();
            }
        }
    });

    window.addEventListener('resize', function() {
        if (window.innerWidth > 992) {
            closeDrawer();
        }
    });
});

function applyResponsiveTables() {
    const tables = document.querySelectorAll('table[data-responsive="cards"], table.responsive-cards');
    tables.forEach(table => {
        if (!table.tHead || !table.tBodies.length) return;
        const headers = Array.from(table.tHead.rows[0].cells).map(th => th.innerText.trim());
        Array.from(table.tBodies[0].rows).forEach(row => {
            Array.from(row.cells).forEach((td, idx) => {
                if (!td.getAttribute('data-label')) {
                    td.setAttribute('data-label', headers[idx] || '');
                }
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', applyResponsiveTables);
