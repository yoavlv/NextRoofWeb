// Function to save the selected street value to localStorage
function saveSelectedStreet(value) {
    localStorage.setItem('selectedStreet', value);
}

// Function to retrieve the selected street value from localStorage
function getSelectedStreet() {
    return localStorage.getItem('selectedStreet');
}

// Retrieve the selected street value and set it as the default value in the select field
document.addEventListener('DOMContentLoaded', function() {
    var selectedStreet = getSelectedStreet();
    if (selectedStreet) {
        var streetSelect = document.getElementById('street_id');
        streetSelect.value = selectedStreet;
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const buyElement = document.querySelector('.buy');
    const saleElement = document.querySelector('.sale');

    if (window.location.href.includes('asset_value')) {
        saleElement.classList.add('active');
    } else {
        buyElement.classList.add('active');
    }

    buyElement.addEventListener('click', function() {
        setActiveState(buyElement, saleElement);
    });

    saleElement.addEventListener('click', function() {
        setActiveState(saleElement, buyElement);
    });

    function setActiveState(toActivate, toDeactivate) {
        toActivate.classList.add('active');
        toDeactivate.classList.remove('active');
    }
});
