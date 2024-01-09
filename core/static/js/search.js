function saveSelectedCity(value) {
    localStorage.setItem('selectedCity', value);
    fetchAndUpdateNeighborhoods(value);
}

function saveSelectedNeighborhood(value) {
    localStorage.setItem('selectedNeighborhood', value);
    fetchAndUpdateStreets(value);
}

function getSelectedCity() {
    return localStorage.getItem('selectedCity');
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
            neighborhoodSelect.innerHTML = '';
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
            streetSelect.innerHTML = '';
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


function toggleMoreOptions(event) {
    event.preventDefault();  // Prevents the form from submitting when the button is clicked
    const toggleButton = event.target;
    const searchRectangle = document.getElementById("search-rectangle")
    const moreOptions = document.getElementById("more-options-section");
    const isMobileView = window.innerWidth <= 768;
    if (moreOptions.style.display === "none" || moreOptions.style.display === "") {
        moreOptions.style.display = "flex";
        toggleButton.innerText = "הצג פחות";
        localStorage.setItem("moreOptionsState", "expanded");
        if (isMobileView) {
           searchRectangle.style.minHeight = '35.7rem';
        }
        else {
            searchRectangle.style.minHeight = '25rem';
        }
    } else {
        moreOptions.style.display = "none";
        toggleButton.innerText = "חיפוש מתקדם";
        localStorage.setItem("moreOptionsState", "collapsed");
        if (isMobileView) {
           searchRectangle.style.minHeight = '29rem';
        }
        else {
            searchRectangle.style.minHeight = '20rem';
        }
    }
};

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
};

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
};


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


document.addEventListener("DOMContentLoaded", function() {
    const expectedUrl = "http://127.0.0.1:8000/search/";
    const expectedUrl2 = "https://www.nextroof.co.il/search/";
    if (window.location.href === expectedUrl || window.location.href === expectedUrl2) {
        document.getElementById("city").value = 'בחר עיר';
        document.getElementById("neighborhood").value = 'בחר שכונה';
        document.getElementById("street").value = 'בחר רחוב';


    }
});

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
    var img = button.querySelector('.like-icon');

    // Perform an AJAX call to toggle like status
    fetch(`/toggle_like/${itemId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else if (response.status === 403) {
            window.location.href = '/login/';
        } else {
            throw new Error('Something went wrong');
        }
    })
    .then(data => {
        if (data && data.liked) {
            img.src = staticPaths.likedImg;  // Use the path from the staticPaths object
        } else {
            img.src = staticPaths.likeImg;  // Use the path from the staticPaths object
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
};

window.onload = function() {
    var savingElements = document.querySelectorAll('.saving');
    savingElements.forEach(function(element) {
            if (element.innerHTML.includes('-')) {
                element.style.color = 'red';
                element.innerHTML = element.innerHTML.replace('חיסכון:', '');
                element.innerHTML = element.innerHTML.replace('-', '');


            } else {
                element.style.color = 'green';
            }
        });
};
