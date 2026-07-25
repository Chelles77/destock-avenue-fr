// Toggle password visibility
document.addEventListener('DOMContentLoaded', function() {
  // Trouver tous les champs password
  const passwordFields = document.querySelectorAll('input[type="password"]');

  passwordFields.forEach(field => {
    // Créer le conteneur wrapper
    const wrapper = document.createElement('div');
    wrapper.className = 'password-wrapper';

    // Créer le bouton oeil
    const toggleBtn = document.createElement('button');
    toggleBtn.type = 'button';
    toggleBtn.className = 'password-toggle';
    toggleBtn.innerHTML = '👁️';
    toggleBtn.setAttribute('aria-label', 'Afficher/Masquer le mot de passe');

    // Insérer le wrapper avant le champ
    field.parentNode.insertBefore(wrapper, field);

    // Déplacer le champ dans le wrapper
    wrapper.appendChild(field);
    wrapper.appendChild(toggleBtn);

    // Ajouter l'event listener pour le toggle
    toggleBtn.addEventListener('click', function(e) {
      e.preventDefault();
      const isPassword = field.type === 'password';
      field.type = isPassword ? 'text' : 'password';
      toggleBtn.innerHTML = isPassword ? '🙈' : '👁️';
    });
  });

  // Ajoute le bouton Ecommerce à la navbar
  function addEcommerceBtn() {
    const navLinks = document.querySelector('.navbar .nav-links');
    if (navLinks && !document.querySelector('a[href*="localhost:3001/publish"]')) {
      const link = document.createElement('a');
      link.href = 'http://localhost:3001/publish.html';
      link.textContent = '📤 Ecommerce';
      link.style.cssText = 'color: #4ade80 !important; font-weight: 600; background: #064e3b; padding: 0.5rem 0.75rem; border-radius: 0.375rem;';
      link.title = 'Publier sur le site ecommerce';

      // Insère avant le lien Déconnexion
      const decoLink = navLinks.querySelector('a[href*="/auth/logout"]');
      if (decoLink) {
        decoLink.parentNode.insertBefore(link, decoLink);
      }
    }
  }

  // Essaie plusieurs fois avec des délais croissants
  setTimeout(addEcommerceBtn, 100);
  setTimeout(addEcommerceBtn, 500);
  setTimeout(addEcommerceBtn, 1000);
});
