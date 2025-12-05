// Populate dropdown
const wardSelect = document.getElementById("wardSelect");
const heatwaveBox = document.getElementById("heatwaveBox");

Object.keys(WARD_DATA).forEach(ward => {
    const option = document.createElement("option");
    option.value = ward;
    option.textContent = ward;
    wardSelect.appendChild(option);
});

// Chart.js setup
const ctx = document.getElementById('tempChart').getContext('2d');
let factorChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ["Temp_2m", "Humidity", "Green Cover %", "Traffic Index", "AIQ", "Precipitation mm"],
        datasets: [{
            label: 'Values',
            data: [],
            backgroundColor: [
                'rgba(231, 76, 60, 0.7)',
                'rgba(52, 152, 219, 0.7)',
                'rgba(46, 204, 113, 0.7)',
                'rgba(241, 196, 15, 0.7)',
                'rgba(155, 89, 182, 0.7)',
                'rgba(26, 188, 156, 0.7)'
            ]
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: false },
            title: { display: true, text: 'Heat Wave Factors for Selected Taluk' }
        },
        scales: { y: { beginAtZero: true } }
    }
});

// Function to calculate heatwave percentage
function calculateHeatwavePercentage(data) {
    const tempWeight = 0.4;
    const humidityWeight = 0.1;
    const greenCoverWeight = -0.1; // more green cover reduces heatwave
    const trafficWeight = 0.2;
    const aiqWeight = 0.2;
    const precipitationWeight = -0.1; // more rain reduces heatwave

    let score = 
        data.Temp_2m * tempWeight +
        data.Humidity * humidityWeight +
        data.Green_Cover_ * greenCoverWeight +
        data.Traffic_Index * trafficWeight +
        data.AIQ * aiqWeight +
        data.Precipitation_mm * precipitationWeight;

    let percentage = Math.min(Math.max(Math.round(score), 0), 100);
    return percentage;
}

// Update chart and heatwave box on taluk selection
wardSelect.addEventListener("change", function() {
    const ward = this.value;
    if (ward && WARD_DATA[ward]) {
        const data = WARD_DATA[ward];

        // Update chart
        factorChart.data.datasets[0].data = [
            data.Temp_2m,
            data.Humidity,
            data.Green_Cover_,
            data.Traffic_Index,
            data.AIQ,
            data.Precipitation_mm
        ];
        factorChart.update();

        // Update heatwave percentage
        const heatwavePercent = calculateHeatwavePercentage(data);
        heatwaveBox.textContent = `Heatwave: ${heatwavePercent}%`;
    } else {
        factorChart.data.datasets[0].data = [];
        factorChart.update();
        heatwaveBox.textContent = "Heatwave: --%";
    }
});
