document.addEventListener("DOMContentLoaded", function() {
    const newsletter = document.querySelector('.newsletter');
    const aboutUs = document.querySelector('.about-us');

    // Function to add animation classes based on element visibility
    function checkVisibilityAndAnimate(element, className) {
        if (!element) return; // Guard clause in case the element is not found

        const rect = element.getBoundingClientRect();
        // Check if the element is visible within the viewport
        const isVisible = rect.top < window.innerHeight && rect.bottom >= 0 && !element.classList.contains(className);

        if (isVisible) {
            element.classList.add(className); // Apply animation only if element is visible and animation class has not been added before
        }
    }
    function animateOnScroll() {
        checkVisibilityAndAnimate(newsletter, 'slide-up');
        checkVisibilityAndAnimate(aboutUs, 'slide-up');

    }

    // Listen for scroll events
    window.addEventListener('scroll', animateOnScroll);

    animateOnScroll();
});

window.addEventListener('load', (event) => { // Changed to 'load' to ensure all page elements are fully loaded
    if (window.location.hash === '#home-map') {
      setTimeout(() => { // Timeout to ensure smooth scroll after full page load
        const mapSection = document.querySelector('.home-map');
        if (mapSection) {
          mapSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      }, 100); // Small delay to ensure smooth scrolling
    }
  });
