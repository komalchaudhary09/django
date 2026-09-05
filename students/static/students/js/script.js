document.addEventListener('DOMContentLoaded', function () {
    console.log('Student Management System loaded successfully.');

    const navLinks = document.querySelectorAll('nav a');
    const currentPath = window.location.pathname;

    navLinks.forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = '#3498db';
            link.style.fontWeight = 'bold';
        }
    });
});
