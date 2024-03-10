function buttonClicked(timeRange) {
    console.log('Inline button clicked for:', timeRange); // Diagnostic log
    updateChart(timeRange);
}

function updateChartWithData(topCitiesData) {
    const labels = topCitiesData.map(item => item[1]);
    const counts = topCitiesData.map(item => item[2]);
    const ctx = document.getElementById('top-cities-chart').getContext('2d');

    if (window.myChart) {
        window.myChart.destroy(); // Destroy existing chart if it exists
    }

    window.myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Top Cities Searched',
                data: counts,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateChart(timeRange) {
    console.log('Updating chart for:', timeRange); // Diagnostic log
    fetch(`/fetch_data/?time_range=${timeRange}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            console.log('Data received:', data); // Confirm data is received
            updateChartWithData(data.top_cities_data);
            document.getElementById('searches-info').textContent = `Number of Searches: ${data.searches_count}`;
            document.getElementById('entrances-info').textContent = `Number of Entrances: ${data.entrances_count}`;
        })
        .catch(error => console.error('Error fetching data:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.time-btn').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default action
            const timeRange = this.id.replace('-btn', '');
            console.log('Button clicked for:', timeRange); // Log click
            buttonClicked(timeRange); // Call buttonClicked function
        });
    });
});
