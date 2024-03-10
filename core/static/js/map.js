// Initialize the map with a view over Israel
var map = L.map('map').setView([32.0695, 34.87254], 11);
// Set up the tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Define global variables
var markers = [], currentMarker = null, cityBoundaryLayer = null, polygonsLayerGroup = L.layerGroup().addTo(map);
var legend = L.control({position: 'topright'});

function displayMessage(message) {
    const searchContainer = document.getElementById('searchContainer');
    const errorMessageDiv = document.createElement('div');
    errorMessageDiv.id = 'errorMessage';
    errorMessageDiv.className = 'errorMessage';
    errorMessageDiv.textContent = message;
    searchContainer.appendChild(errorMessageDiv);
}


function checkAvailability(city, street) {
    // Case when both city and street are provided
    if (city && street) {
        const dataUrl = `/check_for_street/${encodeURIComponent(city)}/${encodeURIComponent(street)}`;
        return fetch(dataUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`הכתובת אינה זמינה ${city}, ${street}`);
                }
                return response.json();
            })
            .catch(error => {
                throw error; // Rethrow after displaying so it can be handled or logged elsewhere if necessary
            });

    // Case when only city is provided
    } else if (city) {
        const dataUrl = `/check_for_city/${encodeURIComponent(city)}`;
        return fetch(dataUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`העיר ${city} אינה זמינה`);
                }
                return response.json();
            })
            .catch(error => {
                throw error; // Rethrow after displaying so it can be handled or logged elsewhere if necessary
            });

    // Error cases: either street is provided without city, or neither is provided
    } else if (street) {
        // If street is provided but city is not
        const errorMessage = 'אנא הזן עיר';
        return Promise.reject(new Error(errorMessage));
    } else {
        // Neither city nor street is provided
        const errorMessage = 'הכתובת לא תקינה';
        return Promise.reject(new Error(errorMessage));
    }
}

document.getElementById('searchForm').onsubmit = function(e) {
    e.preventDefault();
    polygonsLayerGroup.clearLayers();

     // Clear existing error messages

    const searchContainer = document.getElementById('searchContainer');
    const errorMessage = document.getElementById('errorMessage');
    if (searchContainer &&  searchContainer.lastChild && errorMessage) {
        searchContainer.removeChild(searchContainer.lastChild);
    }

    const city = document.getElementById('city_map').value;
    const street = document.getElementById('street_map').value;

    // Clear existing markers and layers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    if (cityBoundaryLayer) {
        map.removeLayer(cityBoundaryLayer);
        cityBoundaryLayer = null;
    }

    // Initialize plot images for a new search
    let cityPlotImage = null;
    let streetPlotImage = null;
    let lastDealsData = null;

    checkAvailability(city, street)
        .then(data => {

            const cityId = data.city_id;
            const streetId = data.hasOwnProperty('street_id') ? data.street_id : null;
            const last_deals = data.hasOwnProperty('last_deals') ? data.last_deals : null;

            if (!cityId) {
                var errorMessage = 'הכתובת לא תקינה'
                displayMessage(errorMessage)
                return; // Early return if cityId is falsy
            }


            var url = `https://nominatim.openstreetmap.org/search?format=json&country=israel&city=${encodeURIComponent(city)}&polygon_geojson=1`;
            if (streetId) {
                url += `&street=${encodeURIComponent(street)}`;
            }

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.length === 0) {
                        const errorMessage = 'הכתובת לא נמצאה';
                        displayMessage(errorMessage)
                        return;
                    }

                    const latLng = new L.LatLng(data[0].lat, data[0].lon);
                    const marker = L.marker(latLng).addTo(map);
                    map.setView(marker.getLatLng(), 13);

                    const popupContent = document.createElement('div');
                    popupContent.className = 'custom-popup';
                    const plotDiv = document.createElement('div');
                    plotDiv.className = 'plot-div'; // Make sure to set this class

                    popupContent.appendChild(plotDiv);

                    function loadPlot(plotType) {
                        plotDiv.innerHTML = ''; // Clear existing plots
                        let plotImageBase64 = plotType === 'city' ? cityPlotImage : streetPlotImage;

                        if (plotImageBase64) {
                            displayPlotImage(plotImageBase64, plotType);
                        } else {
                            const plotUrl = plotType === 'city' ?
                                `/city_plot_map/${encodeURIComponent(cityId)}/${encodeURIComponent(city)}` :
                                `/street_plot_map/${encodeURIComponent(cityId)}/${encodeURIComponent(city)}/${encodeURIComponent(streetId)}/${encodeURIComponent(street)}`;

                            fetch(plotUrl)
                                .then(response => response.text())
                                .then(base64 => {
                                    plotImageBase64 = base64; // Update variable with fetched data
                                    displayPlotImage(plotImageBase64, plotType);

                                    if (plotType === 'city') {
                                        cityPlotImage = base64;
                                    } else if (plotType === 'street') {
                                        streetPlotImage = base64;
                                    }
                                });
                        }
                    }

                    function displayPlotImage(base64, plotType) {
                        const plotImage = document.createElement('img');
                        plotImage.src = "data:image/png;base64," + base64;
                        plotImage.alt = `${plotType} Plot`;
                        plotImage.className = 'plot-image';
                        plotDiv.appendChild(plotImage);
                    }

                    // Add buttons to switch between city and street plots
                    const buttonRow = document.createElement('div');
                    buttonRow.className = 'button-row-map';

                    // Always add the city button
                    const cityButton = document.createElement('button');
                    cityButton.className = 'button-choose';
                    cityButton.innerText = 'עיר';
                    cityButton.addEventListener('click', () => loadPlot('city'));
                    buttonRow.appendChild(cityButton);

                    // Add the street button and last_deals only if the user has searched for a street
                    if (street) {
                        const streetButton = document.createElement('button');
                        streetButton.className = 'button-choose';
                        streetButton.innerText = 'רחוב';
                        streetButton.addEventListener('click', () => loadPlot('street'));
                        buttonRow.appendChild(streetButton);
                        // last last_deals Button

                        const lastDealsButton = document.createElement('button');
                        lastDealsButton.className = 'button-choose';
                        lastDealsButton.innerText = 'עסקאות';
                        lastDealsButton.addEventListener('click', () => displayLastDeals(city, street, popupContent)); // Pass city and street
                        buttonRow.appendChild(lastDealsButton);

                    }

                    popupContent.appendChild(buttonRow);
                    marker.bindPopup(popupContent);
                    marker.on('click', function() {
                        if (currentMarker) {
                            currentMarker.closePopup();
                        }
                        marker.openPopup();
                        currentMarker = marker;
                        loadPlot('city');
                    });

                    markers.push(marker);

                    // Optionally add city boundary layer
                    if (data[0].geojson) {
                        cityBoundaryLayer = L.geoJSON(data[0].geojson, {
                            color: "blue",
                            weight: 2,
                            opacity: 1,
                            fillOpacity: 0.5
                        }).addTo(map);
                        map.fitBounds(cityBoundaryLayer.getBounds());
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        })
        .catch(error => {
            displayMessage(error.message)
        });
};

var dealsDataCache = {};

function displayLastDeals(city, street, popupContent) {
    const cacheKey = city + "_" + street;

    // Check if data is in cache
    if (dealsDataCache[cacheKey]) {
        // Data is already fetched, use it to display last deals
        const lastDeals = dealsDataCache[cacheKey];
        createLastDealsGrid(lastDeals, popupContent);
    } else {
        // Data is not in cache, fetch it
        const dataUrl = `/check_for_street/${encodeURIComponent(city)}/${encodeURIComponent(street)}`;

        fetch(dataUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('The address was not found.');
                }
                return response.json();
            })
            .then(data => {
                // Store fetched data in cache
                dealsDataCache[cacheKey] = data.last_deals;
                createLastDealsGrid(data.last_deals, popupContent);
            })
            .catch(error => {
                console.error('Error fetching or displaying last deals:', error);
            });
    }
}
function createLastDealsGrid(lastDeals, popupContent) {
    if (!lastDeals || lastDeals.length === 0) {
        console.Error('No last deals found for the specified address.');
        return;
    }

    const plotDiv = popupContent.querySelector('.plot-div');
    plotDiv.innerHTML = ''; // Reset the plotDiv content

    popupContent.style.width = '700px';
    popupContent.style.height = 'auto';

    // Create a container for the last deals grid
    const gridContainer = document.createElement('div');
    gridContainer.className = 'last-deals-grid';

    // Add a header or title for the grid
    const gridTitle = document.createElement('div');
    gridTitle.className = 'grid-title';
    gridTitle.textContent = 'עסקאות אחרונות';
    gridContainer.appendChild(gridTitle);

    // Create the grid header
    const headerRow = document.createElement('div');
    headerRow.className = 'grid-row header';
    headerRow.innerHTML = `
        <div>תאריך</div>
        <div>עיר</div>
        <div>רחוב</div>
        <div>מספר בית</div>
        <div>סוג</div>
        <div>חדרים</div>
        <div>קומה</div>
        <div>שנת בנייה</div>
        <div>גודל</div>
        <div>מחיר</div>`;
    gridContainer.appendChild(headerRow);

    // Populate the grid with last deals data
    lastDeals.forEach(deal => {
        const row = document.createElement('div');
        row.className = 'grid-row';
        row.innerHTML = `
            <div>${deal.date}</div>
            <div>${deal.city}</div>
            <div>${deal.street}</div>
            <div>${deal.home_number}</div>
            <div>${deal.type}</div>
            <div>${deal.rooms}</div>
            <div>${deal.floor}</div>
            <div>${deal.build_year}</div>
            <div>${deal.size} מ"ר</div>
            <div>${deal.price}</div>`;
        gridContainer.appendChild(row);
    });

    // Append the grid to the plotDiv
    plotDiv.appendChild(gridContainer);

    if (currentMarker && currentMarker.getPopup()) {
        currentMarker.getPopup().update();
    }
}

function processPolygon(polygonObject) {
    // Ensure the 'polygon' property exists and is not null
    if (polygonObject && polygonObject.polygon) {
        // Parse the polygon string into an array of coordinates
        var polygonCoordinates = JSON.parse(polygonObject.polygon);

        // Check if the coordinates are valid
        if (Array.isArray(polygonCoordinates) && polygonCoordinates.length > 0) {
            // Check if the coordinates are in the correct format
            if (Array.isArray(polygonCoordinates[0]) && Array.isArray(polygonCoordinates[0][0])) {
                // Coordinates are already in the correct format
                return polygonCoordinates;
            } else {
                // Modify the coordinates to be in the correct format
                var modifiedPolygon = [[[polygonCoordinates[0], polygonCoordinates[1]]]];
                return modifiedPolygon;
            }
        }
    }

    // If the polygon doesn't meet the condition, return null or handle it accordingly
    return null;
}

var polygonsLayerGroup = L.layerGroup(); // Create a layer group to store polygons



function getColorByRank(rank) {
    // Assuming rank is normalized between 100 (min) and 500 (max)
    var normalizedRank = (rank - minRank) / (maxRank - minRank);

    // Convert normalized rank to a color from blue (0) to red (1)
    var red = normalizedRank * 255;     // More red for higher rank
    var blue = (1 - normalizedRank) * 255; // More blue for lower rank
    var green = 0; // No green component

    return `rgb(${Math.round(red)}, ${Math.round(green)}, ${Math.round(blue)})`;
}


function drawPolygons(polygonsData) {
    polygonsLayerGroup.clearLayers();

    polygonsData.forEach(function (polygonObject) {
        var modifiedPolygon = processPolygon(polygonObject);
        if (modifiedPolygon) {
            var polygon = L.polygon(modifiedPolygon);

            // Determine color based on rank
            var polygonColor = getColorByRank(polygonObject.rank);

            var style = {
                color: 'black',        // Border color
                fillColor: polygonColor,
                opacity: 1,
                fillOpacity: 0.6,
                weight: 1,
            };

            polygon.setStyle(style);
            var formatter = new Intl.NumberFormat('he-IL', {
                style: 'currency',
                currency: 'ILS',
                minimumFractionDigits: 0,
            });
            // Bind a tooltip to the polygon to show rank and city name
            var tooltipContent = polygonObject.city_name + "<br>מחיר ממוצע למטר: " + formatter.format(polygonObject.rank);
            polygon.bindTooltip(tooltipContent, {
                direction: 'center',
                className: 'polygon-label'
            });

            polygon.addTo(polygonsLayerGroup);
        } else {
            console.log("Polygon does not meet the condition:", polygonObject);
        }
    });

    polygonsLayerGroup.addTo(map);
}

function toggleTooltips() {
    var currentZoom = map.getZoom();
    var mapBounds = map.getBounds();

    polygonsLayerGroup.eachLayer(function(layer) {
        if (currentZoom > 12 && mapBounds.intersects(layer.getBounds())) {
            // Show tooltip if the polygon is within the current map bounds and zoom level is less than 15
            layer.openTooltip();
        } else {
            // Hide tooltip otherwise
            layer.closeTooltip();
        }
    });
}

// Add zoom level listener to the map
map.on('zoomend', function() {
    var currentZoom = map.getZoom();
    toggleTooltips(currentZoom);
});
map.on('zoomend moveend', toggleTooltips);


document.getElementById('loadPolygonsButton').addEventListener('click', function() {
    // Check if the polygons layer group is already on the map
    if (map.hasLayer(polygonsLayerGroup)) {
        // Remove the layer group from the map
        map.removeLayer(polygonsLayerGroup);
    } else {
        // Load polygons when the button is clicked
        drawPolygons(polygonsData);
    }
});



function updateMapForYear() {
    var selectedYear = document.getElementById('year').value;
    var requestURL = `/update_map/?year=${selectedYear}`;

    fetch(requestURL)
        .then(response => {
            if (!response.ok) {
                response.text().then(text => console.log(text)); // Log the HTML response
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Assuming 'data' contains the polygons data and max/min ranks for the selected year
            polygonsData = data.polygons;
            maxRank = data.max_rank;
            minRank = data.min_rank;

            updateLegend(minRank,maxRank); // update the

            // Clear existing polygons and draw new ones
            if (map.hasLayer(polygonsLayerGroup)) {
                map.removeLayer(polygonsLayerGroup); // Remove the existing layer group from the map
            }
            polygonsLayerGroup = L.layerGroup(); // Create a new layer group
            drawPolygons(polygonsData);
            polygonsLayerGroup.addTo(map); // Add the new layer group to the map
        })
        .catch(error => {
            console.error('Error fetching updated polygons:', error);
        });
}


function updateLegend(min,max) {
    // Remove the existing legend if it exists
    legend.remove();
    // Update legend content or recreate it based on new maxRank and minRank
    legend.onAdd = function(map) {
        var div = L.DomUtil.create('div', 'info legend');
        // Update your gradientCSS and formatter logic here based on new maxRank and minRank
        var gradientCSS = `background: linear-gradient(to top, ${getColorByRank(min)} 0%, ${getColorByRank(max)} 100%);`;

        var formatter = new Intl.NumberFormat('he-IL', {
          style: 'currency',
          currency: 'ILS',
          minimumFractionDigits: 0,
            });
        var legendHTML = `
              <div style="padding: 5px; background: rgba(255, 255, 255, 0.8); border: 1px solid #777; border-radius: 5px;">
                <div style="width: 20px; height: 100px; ${gradientCSS}"></div>
                <div style="text-align: left; font-size: 12px; margin-top: 5px;">
                <h3>מחיר למטר ₪</h3>
                  <div>${formatter.format(maxRank)} (אדום)</div>
                  <div style="position: flex; top: 80px;">${formatter.format(minRank)} (כחול)</div>
                </div>
              </div>
            `;

        div.innerHTML = legendHTML;
        return div;
    };
    legend.addTo(map);
}

document.getElementById('polyForm').addEventListener('submit', function(event) {
    event.preventDefault();
    updateMapForYear();
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
});
