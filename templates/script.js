const menuToggle = document.getElementById('menu-toggle');
      const navLinks = document.getElementById('nav-links');
    
      menuToggle.addEventListener('click', function() {
        navLinks.classList.toggle('hidden');
        menuToggle.classList.toggle('rotate-90');
        const isOpen = !navLinks.classList.contains('hidden');
        const openMenuPath = 'M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z';
        const closedMenuPath = 'M4 8h16M4 16h16';
        const openMenuClass = 'menu-open';
        const closedMenuClass = 'menu-closed';
    
        // Toggle the icon to show/hide the menu
        const menuIcon = menuToggle.querySelector('svg');
        menuIcon.querySelector(`.${openMenuClass}`).classList.toggle('hidden', isOpen);
        menuIcon.querySelector(`.${closedMenuClass}`).classList.toggle('hidden', !isOpen);
        menuIcon.setAttribute('viewBox', isOpen ? '0 0 24 24' : '0 0 20 20');
        menuIcon.setAttribute('width', isOpen ? '24' : '20');
        menuIcon.setAttribute('height', isOpen ? '24' : '20');
        menuIcon.querySelector('path').setAttribute('d', isOpen ? openMenuPath : closedMenuPath);
      });