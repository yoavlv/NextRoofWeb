var radiusSearchEnabled = false;
var searchCircle = null;
var searchMarker = null;

// Function to toggle radius search mode
function enableRadiusSearch(enable) {
    radiusSearchEnabled = enable;
    if (!enable && searchCircle && searchMarker) {
        map.removeLayer(searchCircle);
        map.removeLayer(searchMarker);
    }
}

// Function to update the radius value label as the slider is moved
function updateRadiusValue(value) {
    document.getElementById('radiusValue').innerText = parseFloat(value).toFixed(1);
}

function fetchAndProcessPoint(lat, lng, radius) {
    const dataUrl = `/point/${lat}/${lng}/${radius}/`; // Adjust to your URL
    fetch(dataUrl, {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        console.log("Fetched data:", data); // Debug: Inspect the structure of fetched data

        // Directly use the data if it's an array
        console.log(data)
        if (Array.isArray(data)) {
            // Correctly recognized as an array
            createPointDealsGrid(data);
        } else {
            // Data is not in the expected array format
            console.error('Received data is not an array:', data);
        }
    })
    .catch(error => console.error('Error fetching data:', error));
}
// Enhanced showTab function to manage tab content display and enable radius search mode appropriately
function showTab(tabId) {
    var tabContents = document.getElementsByClassName("tab-content");
    for (var i = 0; i < tabContents.length; i++) {
        tabContents[i].style.display = "none";
    }
    document.getElementById(tabId).style.display = "block";
    enableRadiusSearch(tabId === 'radiusSearch');
}

document.addEventListener('DOMContentLoaded', function() {
    map.on('click', function(e) {
        if (radiusSearchEnabled) {
            var radius = parseFloat(document.getElementById('radiusSlider').value) * 1000;

            // Place a marker if not already present
            if (searchMarker) map.removeLayer(searchMarker);
            searchMarker = L.marker(e.latlng).addTo(map);

            // Draw a circle to represent the radius
            if (searchCircle) map.removeLayer(searchCircle);
            searchCircle = L.circle(e.latlng, { radius: radius }).addTo(map);

            // Send the pin's coordinates and radius to the backend
            fetchAndProcessPoint(e.latlng.lat, e.latlng.lng, radius);


        }
    });
    function updateSearchMarkerAndCircle(latlng, radius) {
        // Remove existing marker and circle if they exist
        if (searchMarker) map.removeLayer(searchMarker);
        if (searchCircle) map.removeLayer(searchCircle);

        // Create a draggable marker and add it to the map
        searchMarker = L.marker(latlng, {draggable: true}).addTo(map);
        searchMarker.on('dragend', function(e) {
            var newLatlng = e.target.getLatLng();
            if (searchCircle) searchCircle.setLatLng(newLatlng); // Update the position of the circle to match the marker
            fetchAndProcessPoint(newLatlng.lat, newLatlng.lng, radius); // Refetch data with the new marker position
        });

        // Draw a circle to represent the radius
        searchCircle = L.circle(latlng, {radius: radius}).addTo(map);

        // Send the pin's coordinates and radius to the backend
        fetchAndProcessPoint(latlng.lat, latlng.lng, radius);
    }

    // Open the default tab
    showTab('polyForm');
});

function createPointDealsGrid(lastDeals) {
    // Ensure there are deals to display
    if (!lastDeals || lastDeals.length === 0) {
        console.error('No last deals found for the specified address.');
        return;
    }
    legend.remove();
    polygonsLayerGroup.clearLayers();
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    const popupContent = document.createElement('div');
    const plotDiv = document.createElement('div');
    plotDiv.className = 'plot-div';
    popupContent.appendChild(plotDiv);

    popupContent.style.width = '735px';
    popupContent.style.height = 'auto';

    const gridContainer = document.createElement('div');
    gridContainer.className = 'last-deals-grid';
    const gridTitle = document.createElement('div');
    gridTitle.className = 'grid-title';
    gridTitle.textContent = 'עסקאות אחרונות';
    gridContainer.appendChild(gridTitle);

    const headerRow = document.createElement('div');
    headerRow.className = 'grid-row header';
    headerRow.innerHTML = `
        <div>תאריך</div>
        <div>מחיר</div>
        <div>עיר</div>
        <div>רחוב</div>
        <div>מספר בית</div>
        <div>סוג</div>
        <div>חדרים</div>
        <div>קומה</div>
        <div>שנת בנייה</div>
        <div>גודל</div>`;
    gridContainer.appendChild(headerRow);

    // Check the number of deals and adjust the grid container style if more than 8 deals
    if (lastDeals.length > 8) {
        gridContainer.style.maxHeight = '400px'; // Adjust maxHeight to your preference
        gridContainer.style.overflowY = 'scroll'; // Enable vertical scrolling
    }

    lastDeals.forEach(deal => {
        const dealRow = document.createElement('div');
        dealRow.className = 'grid-row';
        dealRow.innerHTML = `
            <div>${deal.date}</div>
            <div>${deal.price}</div>
            <div>${deal.city}</div>
            <div>${deal.street}</div>
            <div>${deal.home_number}</div>
            <div>${deal.type}</div>
            <div>${deal.rooms}</div>
            <div>${deal.floor}</div>
            <div>${deal.build_year}</div>
            <div>${deal.size} מ"ר</div>`;
        gridContainer.appendChild(dealRow);
    });

    plotDiv.appendChild(gridContainer);

    if (searchMarker && searchMarker.getPopup()) {
        searchMarker.getPopup().setContent(popupContent).update();
    } else if (searchMarker) {
        searchMarker.bindPopup(popupContent).openPopup();
    }
}
