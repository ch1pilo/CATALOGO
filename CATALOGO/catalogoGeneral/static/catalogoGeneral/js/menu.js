   document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');

    menuToggle.addEventListener('click', function() {
        // Alterna la clase 'active' en el botón para la animación de la 'X'
        this.classList.toggle('active'); 
        // Alterna la clase 'active' en el menú para mostrarlo/ocultarlo con animación
        mobileMenu.classList.toggle('active');
    });
});

document.getElementById('contactForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('¡Gracias por tu mensaje! Te responderemos pronto.');
            // ✅ Redirección directa, más confiable en iOS
            window.location.href = data.url_wasap;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        this.submit(); // Fallback
    });
});