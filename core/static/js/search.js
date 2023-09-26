function saveSelectedCity(value) {
    localStorage.setItem('selectedCity', value);
    fetchAndUpdateNeighborhoods(value);
}

function getSelectedCity() {
    return localStorage.getItem('selectedCity');
}

function saveSelectedNeighborhood(value) {
    localStorage.setItem('selectedNeighborhood', value);
    fetchAndUpdateStreets(value);
}

function getSelectedNeighborhood() {
    return localStorage.getItem('selectedNeighborhood');
}

function saveSelectedStreet(value) {
    localStorage.setItem('selectedStreet', value);
}

function getSelectedStreet() {
    return localStorage.getItem('selectedStreet');
}

function fetchAndUpdateNeighborhoods(city) {
    fetch(`/get-neighborhoods/?city=${encodeURIComponent(city)}`)
        .then(response => response.json())
        .then(data => {
            var neighborhoodSelect = document.getElementById('neighborhood');
            neighborhoodSelect.innerHTML = ''; // Clear existing options
            data.neighborhoods.forEach(function(neighborhood) {
                var option = new Option(neighborhood, neighborhood);
                neighborhoodSelect.add(option);
            });
            neighborhoodSelect.value = getSelectedNeighborhood();
        })
        .catch(error => console.error('Error fetching neighborhoods:', error));
}

function fetchAndUpdateStreets(neighborhood) {
    fetch(`/get-streets/?neighborhood=${encodeURIComponent(neighborhood)}`)
        .then(response => response.json())
        .then(data => {
            var streetSelect = document.getElementById('street');
            streetSelect.innerHTML = ''; // Clear existing options
            data.streets.forEach(function(street) {
                var option = new Option(street, street);
                streetSelect.add(option);
            });
            streetSelect.value = getSelectedStreet();
        })
        .catch(error => console.error('Error fetching streets:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    var selectedCity = getSelectedCity();
    if (selectedCity) {
        var citySelect = document.getElementById('city');
        citySelect.value = selectedCity;
        fetchAndUpdateNeighborhoods(selectedCity);
    }

    var selectedNeighborhood = getSelectedNeighborhood();
    if (selectedNeighborhood) {
        var neighborhoodSelect = document.getElementById('neighborhood');
        neighborhoodSelect.value = selectedNeighborhood;
        fetchAndUpdateStreets(selectedNeighborhood);
    }

    var selectedStreet = getSelectedStreet();
    if (selectedStreet) {
        var streetSelect = document.getElementById('street');
        streetSelect.value = selectedStreet;
    }
});


//function getSelectedNeighborhood() {
//    if (!window.location.href.includes('city')) {
//        localStorage.clear();
//        return;
//    }
//    return localStorage.getItem('selectedNeighborhood');
//}



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
        toggleButton.innerText = "חיפוש מתקדם";
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
    document.getElementById("min-price").addEventListener("input", saveSearchParams);
    document.getElementById("max-price").addEventListener("input", saveSearchParams);
    document.getElementById("min-room-number").addEventListener("input", saveSearchParams);
    document.getElementById("max-room-number").addEventListener("input", saveSearchParams);
    document.getElementById("min-floor").addEventListener("input", saveSearchParams);
    document.getElementById("max-floor").addEventListener("input", saveSearchParams);
    document.getElementById("min-size").addEventListener("input", saveSearchParams);
    document.getElementById("max-size").addEventListener("input", saveSearchParams);
});


document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('city').addEventListener('change', function() {
        var selectedCity = this.value;
        fetch(`{% url 'get-neighborhoods' %}?city=${encodeURIComponent(selectedCity)}`)
            .then(response => response.json())
            .then(data => {
                var neighborhoodSelect = document.getElementById('neighborhood');
                neighborhoodSelect.innerHTML = '';
                neighborhoodSelect.add(new Option('בחר שכונה', ''));

                var streetSelect = document.getElementById('street');
                streetSelect.innerHTML = ''; // Correctly clear the street select
                streetSelect.add(new Option('בחר רחוב', ''));

                data.neighborhoods.forEach(function(neighborhood) {
                    var option = new Option(neighborhood, neighborhood);
                    neighborhoodSelect.add(option);
                });
            })
            .catch(error => console.error('Error fetching neighborhoods:', error));
    });
});


document.addEventListener("DOMContentLoaded", function() {
        document.getElementById('neighborhood').addEventListener('change', function() {
            var selectedNeighborhood = this.value;
            fetch(`{% url 'get-streets' %}?neighborhood=${encodeURIComponent(selectedNeighborhood)}`)
                .then(response => response.json())
                .then(data => {
                    var streetSelect = document.getElementById('street');
                    streetSelect.innerHTML = ''; // Clear existing options
                    streetSelect.add(new Option('בחר רחוב', ''));

                    data.streets.forEach(function(street) {
                        var option = new Option(street, street);
                        streetSelect.add(option);
                    });
                })
                .catch(error => console.error('Error fetching streets:', error));
        });
    });
