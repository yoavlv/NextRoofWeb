function toggleNavBar() {
    var navBar = document.getElementById('nav-bar');
    var body = document.body;
    var hamburgerBtn = document.querySelector('.hamburger-btn');
    navBar.classList.toggle('open');
    navBar.classList.toggle('opening');
    hamburgerBtn.classList.toggle('active');
    body.classList.toggle('no-scroll');
    var navItems = document.querySelectorAll('.nav-container ul li');

    var displayStyle = window.getComputedStyle(navBar).display; // Get computed style

    if (displayStyle === "flex") {
        navBar.style.display = "none";
        body.classList.remove('no-scroll');
        // Reset styles for nav items
        navItems.forEach(item => item.style.opacity = "0");
    } else {
        navBar.style.display = "flex";
        body.classList.add('no-scroll');
        // Animate nav items
        navItems.forEach(item => item.style.opacity = "0");
        navItems.forEach((item, index) => {
            // Set initial position to the left
            item.style.transform = "translateX(-100px)";
            item.style.opacity = "0";
            setTimeout(() => {
                // Animate to the right and then to the center
                item.style.opacity = "1";
                item.style.transform = "translateX(0)";
            }, 100 * (index + 1)); // Delay each item's animation
        });
    }
}
document.querySelector('.hamburger-btn').addEventListener('click', toggleNavBar);

document.addEventListener("DOMContentLoaded", function() {
    const savedState = localStorage.getItem('navbarState');
    if (savedState === "open") {
        const navBar = document.getElementById("nav-bar");
        navBar.style.display = "flex";
        document.body.classList.add('no-scroll');
    }
});

window.addEventListener("scroll", function() {
    const navBar = document.getElementById("nav-bar");
    if (window.pageYOffset > 50) {
        navBar.classList.add("transparent");
    } else {
        navBar.classList.remove("transparent");
    }
});
