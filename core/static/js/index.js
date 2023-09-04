



function openNavBar(event) {
    event.preventDefault();
    const moreOptions = document.getElementById("nav-bar");
    if (moreOptions.style.display === "flex") {
        moreOptions.style.display = "none";
        localStorage.setItem('navbarState', 'closed');
    } else {
        moreOptions.style.display = "flex";
        localStorage.setItem('navbarState', 'open');
    }
}

console.log("DOMContentLoaded event fired");
console.log("savedState value from localStorage:", savedState);

document.addEventListener("DOMContentLoaded", function() {
    const savedState = localStorage.getItem('navbarState');
    const moreOptions = document.getElementById("nav-bar-b");

    if (savedState === "open") {
        moreOptions.style.display = "flex";
    }
    // if savedState is 'closed' or null (i.e., not set), the navbar will be hidden due to the default styles.
});


window.addEventListener("scroll", function() {
    const navBar = document.querySelector("nav");
    if(window.scrollY > 10) {
        navBar.classList.add("transparent-nav");
    } else {
        navBar.classList.remove("transparent-nav");
    }
});
