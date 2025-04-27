// Script principal pour le site de réservation d'activités

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialisation des popovers Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Gestion des messages flash
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Gestion du système de notation par étoiles
    const starRatings = document.querySelectorAll('.star-rating-input');
    starRatings.forEach(function(ratingGroup) {
        const stars = ratingGroup.querySelectorAll('.star');
        const ratingInput = ratingGroup.querySelector('input[type="hidden"]');
        
        stars.forEach(function(star, index) {
            // Au survol
            star.addEventListener('mouseover', function() {
                for (let i = 0; i <= index; i++) {
                    stars[i].classList.add('filled');
                }
                for (let i = index + 1; i < stars.length; i++) {
                    stars[i].classList.remove('filled');
                }
            });
            
            // Au clic
            star.addEventListener('click', function() {
                ratingInput.value = index + 1;
                for (let i = 0; i <= index; i++) {
                    stars[i].classList.add('selected');
                }
                for (let i = index + 1; i < stars.length; i++) {
                    stars[i].classList.remove('selected');
                }
            });
        });
        
        // Quand la souris quitte la zone
        ratingGroup.addEventListener('mouseleave', function() {
            const rating = parseInt(ratingInput.value) || 0;
            stars.forEach(function(star, index) {
                if (index < rating) {
                    star.classList.add('filled');
                } else {
                    star.classList.remove('filled');
                }
            });
        });
    });
    
    // Mise à jour dynamique du total dans le formulaire de réservation
    const reservationForm = document.getElementById('reservation-form');
    if (reservationForm) {
        const participantsInput = document.getElementById('participants');
        const totalElement = document.getElementById('total-price');
        const unitPrice = parseFloat(document.getElementById('unit-price').dataset.price);
        
        participantsInput.addEventListener('input', function() {
            const participants = parseInt(this.value) || 1;
            const total = (unitPrice * participants).toFixed(2);
            totalElement.textContent = total + ' €';
        });
    }
    
    // Filtres dynamiques pour les activités
    const searchForm = document.getElementById('activity-search-form');
    if (searchForm) {
        const minPriceInput = document.getElementById('min_price');
        const maxPriceInput = document.getElementById('max_price');
        
        // Validation des prix
        maxPriceInput.addEventListener('input', function() {
            const minPrice = parseFloat(minPriceInput.value) || 0;
            const maxPrice = parseFloat(this.value) || 0;
            
            if (maxPrice > 0 && maxPrice < minPrice) {
                this.setCustomValidity('Le prix maximum doit être supérieur au prix minimum');
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    // Gestion de la sélection des créneaux horaires
    const timeSlots = document.querySelectorAll('.time-slot-option');
    if (timeSlots.length > 0) {
        const timeSlotInput = document.getElementById('time_slot_id');
        
        timeSlots.forEach(function(slot) {
            slot.addEventListener('click', function() {
                // Ne rien faire si le créneau est désactivé
                if (this.classList.contains('disabled')) {
                    return;
                }
                
                // Désélectionner tous les créneaux
                timeSlots.forEach(s => s.classList.remove('selected'));
                
                // Sélectionner le créneau cliqué
                this.classList.add('selected');
                
                // Mettre à jour la valeur de l'input caché
                timeSlotInput.value = this.dataset.slotId;
            });
        });
    }
    
    // Animation au défilement pour les éléments
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    if (animateElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                }
            });
        }, {
            threshold: 0.1
        });
        
        animateElements.forEach(element => {
            observer.observe(element);
        });
    }
    
    // Initialisation de la date et heure actuelle dans les éléments
    const currentDateElements = document.querySelectorAll('.current-date');
    if (currentDateElements.length > 0) {
        const now = new Date();
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        const formattedDate = now.toLocaleDateString('fr-FR', options);
        
        currentDateElements.forEach(element => {
            element.textContent = formattedDate;
        });
    }
});

// Fonction utilitaire pour formatter le prix
function formatPrice(price) {
    return new Intl.NumberFormat('fr-FR', { 
        style: 'currency', 
        currency: 'EUR'
    }).format(price);
}

// Fonction pour vérifier si un élément est visible dans le viewport
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}
