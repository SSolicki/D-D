// Initialize all Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add confirmation dialog to delete buttons
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Add character form validation
    var characterForm = document.querySelector('#character-form');
    if (characterForm) {
        characterForm.addEventListener('submit', function(e) {
            if (!characterForm.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            characterForm.classList.add('was-validated');
        });
    }

    // Add campaign form validation
    var campaignForm = document.querySelector('#campaign-form');
    if (campaignForm) {
        campaignForm.addEventListener('submit', function(e) {
            if (!campaignForm.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            campaignForm.classList.add('was-validated');
        });
    }

    // Add responsive table wrapper
    document.querySelectorAll('table').forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            var wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
});
