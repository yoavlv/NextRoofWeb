function saveSelectedCityCalc() {
    var selectedCity = document.getElementById('city_calc').value;
    localStorage.setItem('selectedCityCalc', selectedCity);
    fetchAndUpdateStreetsForCityCalc(selectedCity);
}

function getSelectedCityCalc() {
    return localStorage.getItem('selectedCityCalc');
}

function saveSelectedStreetCalc(value) {
    localStorage.setItem('selectedStreetCalc', value);
}

function getSelectedStreetCalc() {
    return localStorage.getItem('selectedStreetCalc');
}

function fetchAndUpdateStreetsForCityCalc(city) {
    fetch(`/get-streets-city/?city=${encodeURIComponent(city)}`)
        .then(response => response.json())
        .then(data => {
            var streetSelect = document.getElementById('street_calc');
            streetSelect.innerHTML = ''; // Clear existing options
            data.streets.forEach(function(street) {
                var option = new Option(street, street);
                streetSelect.add(option);
            });
            streetSelect.value = getSelectedStreetCalc();
        })
        .catch(error => console.error('Error fetching streets:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    var selectedCityCalc = getSelectedCityCalc();
    if (selectedCityCalc) {
        var citySelectCalc = document.getElementById('city_calc');
        citySelectCalc.value = selectedCityCalc;
        fetchAndUpdateStreetsForCityCalc(selectedCityCalc);
    }

    var selectedStreetCalc = getSelectedStreetCalc();
    if (selectedStreetCalc) {
        var streetSelectCalc = document.getElementById('street_calc');
        streetSelectCalc.value = selectedStreetCalc;
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


function saveCalcParams() {
    const params = {
        Rooms: document.getElementById("rooms").value,
        Floor: document.getElementById("floor").value,
        Size: document.getElementById("size").value,
        Parking: document.getElementById("parking").value,
        Condition: document.getElementById("condition").value,
        HomeNumber: document.getElementById("home-number").value,
        Street: document.getElementById("street_calc").value,

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
        document.getElementById("street_calc").value = calcParams.Street || '';

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
    document.getElementById("street_calc").addEventListener("change", saveCalcParams);

});
