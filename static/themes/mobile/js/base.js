
(function() {
  'use strict';

  // Create and inject mobile menu toggle button
  function createMobileToggle() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    const toggle = document.createElement('button');
    toggle.className = 'mobile-menu-toggle';
    toggle.innerHTML = '<span></span><span></span><span></span>';
    toggle.setAttribute('aria-label', 'Toggle menu');
    toggle.setAttribute('aria-expanded', 'false');

    navbar.insertBefore(toggle, navbar.firstChild);
    return toggle;
  }

  // Handle mobile menu toggle
  function initMobileMenu() {
    const toggle = createMobileToggle();
    const navbar = document.querySelector('.navbar');
    const navList = navbar.querySelector('ul');

    if (!toggle || !navList) return;

    toggle.addEventListener('click', function(e) {
      e.stopPropagation();
      const isOpen = navList.classList.toggle('mobile-open');
      toggle.classList.toggle('active');
      toggle.setAttribute('aria-expanded', isOpen);
      document.body.classList.toggle('menu-open', isOpen);
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
      if (!navbar.contains(e.target) && navList.classList.contains('mobile-open')) {
        navList.classList.remove('mobile-open');
        toggle.classList.remove('active');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('menu-open');
      }
    });
  }

  // Handle dropdown behavior
  function initDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(dropdown => {
      const button = dropdown.querySelector('.dropbtn');
      const content = dropdown.querySelector('.dropdown-content');

      if (!button || !content) return;

      // Create a toggle indicator
      const indicator = document.createElement('span');
      indicator.className = 'dropdown-indicator';
      indicator.innerHTML = '▼';
      button.appendChild(indicator);

      button.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();

        // Close other dropdowns
        dropdowns.forEach(other => {
          if (other !== dropdown) {
            other.classList.remove('dropdown-open');
          }
        });

        dropdown.classList.toggle('dropdown-open');
      });
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      initMobileMenu();
      initDropdowns();
    });
  } else {
    initMobileMenu();
    initDropdowns();
  }
})();