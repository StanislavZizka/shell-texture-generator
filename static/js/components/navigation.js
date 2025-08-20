// Navigation Component - Sidebar toggle and interactions
let navOpen = false;

function toggleNav() {
  const sidenav = document.getElementById("mySidenav");
  const main = document.getElementById("main");

  if (navOpen) {
    sidenav.classList.remove('expanded');
    main.classList.remove('expanded');
  } else {
    sidenav.classList.add('expanded');
    main.classList.add('expanded');
  }

  navOpen = !navOpen;
}

// Enhanced navigation with keyboard support and smooth interactions
document.addEventListener('DOMContentLoaded', function() {
  // Keyboard navigation support
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && navOpen) {
      toggleNav();
    }
  });

  // Add smooth hover effects to navigation links
  const navLinks = document.querySelectorAll('.sidenav a');
  navLinks.forEach(link => {
    link.addEventListener('mouseenter', function() {
      this.style.transform = 'translateX(4px)';
    });
    
    link.addEventListener('mouseleave', function() {
      this.style.transform = 'translateX(0)';
    });
  });

  // Add click handler to menu button
  const menuBtn = document.querySelector('.menu-btn');
  if (menuBtn) {
    menuBtn.addEventListener('click', toggleNav);
  }

  // Close navigation when clicking outside on mobile
  document.addEventListener('click', function(e) {
    const sidenav = document.getElementById("mySidenav");
    const isClickInsideNav = sidenav && sidenav.contains(e.target);
    const isMenuButton = e.target.closest('.menu-btn');
    
    if (navOpen && !isClickInsideNav && !isMenuButton && window.innerWidth <= 768) {
      toggleNav();
    }
  });

  // Handle window resize
  window.addEventListener('resize', function() {
    const sidenav = document.getElementById("mySidenav");
    const main = document.getElementById("main");
    
    // Reset navigation state on large screens
    if (window.innerWidth > 768 && navOpen) {
      sidenav.classList.remove('expanded');
      main.classList.remove('expanded');
      navOpen = false;
    }
  });
});

// Global function for external access
function toggleMobileMenu() {
  toggleNav();
}

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { toggleNav, toggleMobileMenu };
}