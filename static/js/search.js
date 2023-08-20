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