//function updateStreetsForSelectedCity() {
//    var selectedCity = document.getElementById('city_calc').value;
//    fetch(`/get-streets-city/?city_calc=${encodeURIComponent(selectedCity)}`)
//        .then(response => response.json())
//        .then(data => {
//            var streetSelect = document.getElementById('street_calc');
//            streetSelect.innerHTML = '<option value="">בחר רחוב</option>';
//            data.streets.forEach(function(street) {
//                streetSelect.add(new Option(street, street));
//            });
//        })
//        .catch(error => console.error('Error:', error));
//}

// Attach this function to the city dropdown's change event
//document.getElementById('city_calc').addEventListener('change', updateStreetsForSelectedCity);


function saveCalcParams() {
    const params = {
        Rooms: document.getElementById("rooms").value,
        Floor: document.getElementById("floor").value,

        Size: document.getElementById("size").value,
        Parking: document.getElementById("parking").value,
        Condition: document.getElementById("condition").value,
        HomeNumber: document.getElementById("home-number").value,
    };

    localStorage.setItem("calcParams", JSON.stringify(params));
}

function loadCalcParams() {
    const calcParams = JSON.parse(localStorage.getItem("calcParams"));
    if (calcParams) {
        document.getElementById("rooms").value = calcParams.Rooms || '';
        document.getElementById("floor").value = calcParams.Floor || '';
        document.getElementById("size").value = calcParams.Size || '';
        document.getElementById("home-number").value = calcParams.HomeNumber || '';
        document.getElementById("parking").value = calcParams.Parking || '0'; // Default to 0 if not set
        document.getElementById("condition").value = calcParams.Condition || '1'; // Default to 1 if not set
    }
}

document.addEventListener("DOMContentLoaded", function() {
    loadCalcParams();
    document.getElementById("rooms").addEventListener("input", saveCalcParams);
    document.getElementById("floor").addEventListener("input", saveCalcParams);
    document.getElementById("size").addEventListener("input", saveCalcParams);
    document.getElementById("home-number").addEventListener("input", saveCalcParams);
    document.getElementById("parking").addEventListener("change", saveCalcParams);
    document.getElementById("condition").addEventListener("change", saveCalcParams);
});


document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.calc-form').addEventListener('submit', function() {
        document.getElementById('loading-popup').style.display = 'flex';
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const buttonGraph = document.querySelector('#graph');
    const buttonLast = document.querySelector('#last-deals');
    const buttonSimilar = document.querySelector('#similar-deals');
    const streetImage = document.querySelector('#street-image');
    const lastDealsContent = document.querySelector('#last-deals-content');
    const similarDealsContent = document.querySelector('#similar-deals-content');
    streetImage.style.display = 'block';
    lastDealsContent.style.display = 'none';
    similarDealsContent.style.display = 'none';
    buttonGraph.addEventListener('click', () => {
      streetImage.style.display = 'block';
      lastDealsContent.style.display = 'none';
      similarDealsContent.style.display = 'none';
    });

    buttonLast.addEventListener('click', () => {
      streetImage.style.display = 'none';
      lastDealsContent.style.display = 'block';
      similarDealsContent.style.display = 'none';
    });

    buttonSimilar.addEventListener('click', () => {
      streetImage.style.display = 'none';
      lastDealsContent.style.display = 'none';
      similarDealsContent.style.display = 'block';
    });
});
