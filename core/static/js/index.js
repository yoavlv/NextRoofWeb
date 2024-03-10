function toggleNavBar() {
    var navBar = document.getElementById('nav-bar');
    var body = document.body;
    var navBar = document.getElementById("nav-bar");

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
window.addEventListener("scroll", function() {
    if (window.innerWidth > 768) { // Check if the screen size is bigger than 768px
        const navBar = document.getElementById("nav-bar");
        const logoImg = document.querySelector('.logo-img'); // Select the logo image
        // Read URLs from data attributes
        const blackLogo = logoImg.getAttribute('data-black');
        const whiteLogo = logoImg.getAttribute('data-white');
        const navItems = document.querySelectorAll('.nav-container ul li a');

        if (window.pageYOffset > 50) {
            navBar.style.backgroundColor = "rgba(9, 30, 40, 0.45)";
            navItems.forEach(item => item.style.color = "white");
            logoImg.src = whiteLogo; // Use white logo
        } else {
            navBar.style.backgroundColor = "transparent";
            navItems.forEach(item => item.style.color = "black");
            logoImg.src = blackLogo; // Use black logo
        }
    }
});


document.querySelector('.hamburger-btn').addEventListener('click', toggleNavBar);
