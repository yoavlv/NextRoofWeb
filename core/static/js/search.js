
document.addEventListener("DOMContentLoaded", function() {
    initializeMoreOptions();
    loadSearchParams();
    attachEventListeners();
    adjustSavingElements()
});

function toggleMoreOptions(event) {
    event.preventDefault(); // Prevent default action of the event
    const moreOptions = document.getElementById("more-options-section");
    const toggleButton = event.target;
    const isExpanded = moreOptions.style.display === "flex";

    moreOptions.style.display = isExpanded ? "none" : "flex";
    toggleButton.innerText = isExpanded ? "חיפוש מתקדם" : "הצג פחות";
    localStorage.setItem("moreOptionsState", isExpanded ? "collapsed" : "expanded");
    adjustSearchRectangleHeight();
}


function adjustSearchRectangleHeight() {
    const searchRectangle = document.getElementById("search-rectangle");
    const isMobileView = window.innerWidth <= 768;
    const moreOptions = document.getElementById("more-options-section");
    const isExpanded = moreOptions.style.display === "flex";

    if (isMobileView) {
        searchRectangle.style.minHeight = isExpanded ? '35.7rem' : '29rem';
    } else {
        searchRectangle.style.minHeight = isExpanded ? '25rem' : '21.5rem';
    }
}

function initializeMoreOptions() {
    const moreOptions = document.getElementById("more-options-section");
    const savedState = localStorage.getItem("moreOptionsState");

    moreOptions.style.display = savedState === "expanded" ? "flex" : "none";
    adjustSearchRectangleHeight();
}

function saveSearchParams() {
    const params = {
        city: document.getElementById("city").value,
        street: document.getElementById("street").value,
        minPrice: document.getElementById("min-price").value,
        maxPrice: document.getElementById("max-price").value,
        minRooms: document.getElementById("min-room-number").value,
        maxRooms: document.getElementById("max-room-number").value,
        minFloor: document.getElementById("min-floor").value,
        maxFloor: document.getElementById("max-floor").value,
        minSize: document.getElementById("min-size").value,
        maxSize: document.getElementById("max-size").value,
    };

    localStorage.setItem("searchParams", JSON.stringify(params));
}

function loadSearchParams() {
    const savedParams = JSON.parse(localStorage.getItem("searchParams"));
    if (savedParams) {
        Object.keys(savedParams).forEach(key => {
            const input = document.getElementById(key.replace('-', '_')); // Adjust the ID if necessary
            if (input && savedParams[key] !== "None") {
                input.value = savedParams[key] || '';
            }
        });
    }
}

function attachEventListeners() {
    document.querySelectorAll("#searchForm input").forEach(input => {
        input.addEventListener("input", saveSearchParams);
    });

    document.getElementById("searchForm").addEventListener("submit", saveSearchParams);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toggleLike(button, itemId) {
    var isLoggedIn = button.getAttribute('data-logged-in') === 'true';

    // If the user is not logged in, redirect to the registration page
    if (!isLoggedIn) {
        window.location.href = "/register/"; // Adjust the URL to your registration page as needed
        return;
    }

    var img = button.querySelector('.like-icon');
    fetch(`/toggle_like/${itemId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.ok ? response.json() : Promise.reject(response))
    .then(data => {
        img.src = data.liked ? staticPaths.likedImg : staticPaths.likeImg;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function adjustSavingElements() {
    document.querySelectorAll('.saving').forEach(function(element) {
        if (element.innerHTML.includes('-')) {
            element.style.color = 'red';
            element.innerHTML = element.innerHTML.replace('חיסכון:', '').replace('-', '');
        } else {
            element.style.color = 'green';
        }
    });
}
