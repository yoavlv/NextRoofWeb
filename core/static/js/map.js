var map = L.map('map').setView([31.0461, 34.8516], 8); // Coordinates for Israel

// Set up the tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

var markers = [];
var currentMarker = null; // Keep track of the currently open marker
var cityBoundaryLayer = null; // Layer for the city boundary

document.getElementById('searchForm').onsubmit = function(e) {
    e.preventDefault();
    polygonsLayerGroup.clearLayers();
    var city = document.getElementById('city_map').value;
    var neighborhood = document.getElementById('neighborhood_map').value;
    var street = document.getElementById('street_map').value;

    if (city) {
        var url = `https://nominatim.openstreetmap.org/search?format=json&country=israel&city=${encodeURIComponent(city)}&polygon_geojson=1`;
        if (street) {
            url += `&street=${encodeURIComponent(street)}`;
        } else if (neighborhood) {
            url += `&county=${encodeURIComponent(neighborhood)}`;
        }

        // Remove existing markers and city boundary layer
        markers.forEach(marker => map.removeLayer(marker));
        markers = [];
        if (cityBoundaryLayer) {
            map.removeLayer(cityBoundaryLayer);
            cityBoundaryLayer = null;
        }

        // Use Nominatim geocoding service to get coordinates and polygon
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    var latLng = new L.LatLng(data[0].lat, data[0].lon);
                    var marker = L.marker(latLng).addTo(map);
                    map.setView(marker.getLatLng(), 13);

                    // Create popup content
                    var popupContent = document.createElement('div');
                    popupContent.className = 'custom-popup';
                    var plotDiv = document.createElement('div');
                    popupContent.appendChild(plotDiv);

                    // Function to load the selected plot
                    function loadPlot(plotType) {
                        plotDiv.innerHTML = ''; // Clear existing plots
                        var plotUrl = '';
                        switch (plotType) {
                            case 'city':
                                plotUrl = `/city_plot_map/${encodeURIComponent(city)}`;
                                break;
                            case 'neighborhood':
                                if (!neighborhood) return; // Prevent fetching if neighborhood is empty
                                plotUrl = `/neighborhood_plot_map/${encodeURIComponent(city)}/${encodeURIComponent(neighborhood)}`;
                                break;
                            case 'street':
                                if (!street) return; // Prevent fetching if street is empty
                                plotUrl = `/street_plot_map/${encodeURIComponent(city)}/${encodeURIComponent(street)}`;
                                break;
                        }

                        fetch(plotUrl)
                            .then(response => response.text())
                            .then(plotImageBase64 => {
                                var plotImage = document.createElement('img');
                                plotImage.src = "data:image/png;base64," + plotImageBase64;
                                plotImage.alt = `${plotType} Plot`;
                                plotImage.className = 'plot-image';
                                plotDiv.appendChild(plotImage);
                            });
                    }

                    // Add buttons to switch between plots
                    var buttonRow = document.createElement('div');
                    buttonRow.className = 'button-row-map';
                    ['city', 'neighborhood', 'street'].forEach(type => {
                        var button = document.createElement('button');
                        button.className = 'button-choose';
                        button.innerText = type === 'city' ? 'עיר' : type === 'neighborhood' ? 'שכונה' : 'רחוב';
                        button.addEventListener('click', () => loadPlot(type));
                        buttonRow.appendChild(button);
                    });
                    popupContent.appendChild(buttonRow);

                    // Bind the popup to the marker
                    marker.bindPopup(popupContent);
                    marker.on('click', function() {
                        if (currentMarker) {
                            currentMarker.closePopup();
                        }
                        marker.openPopup();
                        currentMarker = marker;
                        loadPlot('city'); // Load city plot by default
                    });

                    markers.push(marker);

                    // Add city boundary layer
                    if (data[0].geojson) {
                        console.log(data[0].geojson)
                        cityBoundaryLayer = L.geoJSON(data[0].geojson, {
                            color: "blue",
                            weight: 2,
                            opacity: 1,
                            fillOpacity: 0.5
                        }).addTo(map);
                        map.fitBounds(cityBoundaryLayer.getBounds());
                    }
                } else {
                    alert("City not found");
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("An error occurred while searching for the city");
            });
    } else {
        alert("Please enter a city name");
    }
};



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
                fillOpacity: 0.8,
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

    // Modify the requestURL if your endpoint is different
    var requestURL = `/update_map/?year=${selectedYear}`;

    console.log()
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

document.getElementById('polyForm').addEventListener('submit', function(event) {
    event.preventDefault();
    updateMapForYear();
});
