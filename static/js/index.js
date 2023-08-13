
function saveSelectedNeighborhood(value) {
    localStorage.setItem('selectedNeighborhood', value);
}

// Function to retrieve the selected neighborhood value from localStorage
function getSelectedNeighborhood() {
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





//addEventListener('DOMContentLoaded', () => {
//const selectNeighborhood = document.querySelector('.neighborhood');
//let neighborhoodValue = selectNeighborhood.value;
//console.log(neighborhoodValue);
//selectNeighborhood.addEventListener('change', () => {
//neighborhoodValue = selectNeighborhood.value;
//console.log(neighborhoodValue);
//});});




//addEventListener('DOMContentLoaded', () => {
//const selectNeighborhood = document.querySelector('.neighborhood');
//let neighborhoodValue = selectNeighborhood.value;
//selectNeighborhood.addEventListener('change', () => {
//neighborhoodValue = selectNeighborhood.value;
////console.log(neighborhoodValue);
//const xhr = new XMLHttpRequest();
//xhr.open('GET', `main/asset_value/get_streets/?neighborhood=${neighborhoodValue}`);
//console.log(xhr);
//
//});});

