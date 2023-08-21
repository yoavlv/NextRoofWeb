function saveSelectedNeighborhood(value) {

    localStorage.setItem('selectedNeighborhood', value);
}

// Function to retrieve the selected neighborhood value from localStorage
function getSelectedNeighborhood() {
    if (!window.location.href.includes('city')) {
        localStorage.clear();
        return;
    }
    return localStorage.getItem('selectedNeighborhood');
}



// Retrieve the selected neighborhood value and set it as the default value in the select field
document.addEventListener('DOMContentLoaded', function() {
    var selectedNeighborhood = getSelectedNeighborhood();
    if (selectedNeighborhood) {
        var neighborhoodSelect = document.getElementById('neighborhood_id');
        neighborhoodSelect.value = selectedNeighborhood;
    }
});


function toggleMoreOptions(event) {
    event.preventDefault();  // Prevents the form from submitting when the button is clicked
    const toggleButton = event.target;
    const moreOptions = document.getElementById("more-options-section");

    if (moreOptions.style.display === "none" || moreOptions.style.display === "") {
        moreOptions.style.display = "flex";
        toggleButton.innerText = "הצג פחות";
        localStorage.setItem("moreOptionsState", "expanded");
    } else {
        moreOptions.style.display = "none";
        toggleButton.innerText = "הצגת אופציות נוספות";
        localStorage.setItem("moreOptionsState", "collapsed");
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const moreOptions = document.getElementById("more-options-section");
    const savedState = localStorage.getItem("moreOptionsState");

    if (savedState === "expanded") {
        moreOptions.style.display = "flex";
    } else if (savedState === "collapsed") {
        moreOptions.style.display = "none";
    }
});



function saveSearchParams() {
    const params = {
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
        document.getElementById("min-price").value = savedParams.minPrice || '';
        document.getElementById("max-price").value = savedParams.maxPrice || '';
        document.getElementById("min-room-number").value = savedParams.minRooms || '';
        document.getElementById("max-room-number").value = savedParams.maxRooms || '';
        document.getElementById("min-floor").value = savedParams.minFloor || '';
        document.getElementById("max-floor").value = savedParams.maxFloor || '';
        document.getElementById("min-size").value = savedParams.minSize || '';
        document.getElementById("max-size").value = savedParams.maxSize || '';
    }
}


document.addEventListener("DOMContentLoaded", function() {
    loadSearchParams();  // Load the saved search parameters when the page loads

    // Attach event listeners to each input
    document.getElementById("min-price").addEventListener("input", saveSearchParams);
    document.getElementById("max-price").addEventListener("input", saveSearchParams);
    document.getElementById("min-room-number").addEventListener("input", saveSearchParams);
    document.getElementById("max-room-number").addEventListener("input", saveSearchParams);
    document.getElementById("min-floor").addEventListener("input", saveSearchParams);
    document.getElementById("max-floor").addEventListener("input", saveSearchParams);
    document.getElementById("min-size").addEventListener("input", saveSearchParams);
    document.getElementById("max-size").addEventListener("input", saveSearchParams);
});