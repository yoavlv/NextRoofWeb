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