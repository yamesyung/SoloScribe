const root = document.documentElement;
const fontColor = getComputedStyle(root).getPropertyValue('--font-color').trim();

const plotLayout = {
    autosize: true,
    plot_bgcolor:"rgba( 0, 0, 0, 0)",
    paper_bgcolor:"rgba( 0, 0, 0, 0)",
    legend: {
        font: {
            color: fontColor,
        }
    },
    xaxis: {
        title: 'Year',
        type: 'linear',
        tick0: 0,
        dtick: 25,
        color: fontColor,
    },
    yaxis: {
        title: 'Authors',
        ticks: '',
        showgrid: false,
        showticklabels: false,
        color: fontColor,
    },
};

let plotConfig = {
    displaylogo: false,
    modeBarButtonsToRemove: ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'zoomOut2d', 'zoomIn2d', 'toggleSpikelines'],
    responsive: true
};

const dataPoints = [];

function createChart() {
    Plotly.newPlot('timespanChart', dataPoints, plotLayout, plotConfig);
}

function addPersonToChart(person) {
    const birthYear = new Date(person.birth_date).getFullYear();
    const deathYear = new Date(person.death_date).getFullYear();

    // Treat authors with death year = 1 as currently alive
    const isAlive = deathYear === 1;

    // Add data points for birth year and death year
    dataPoints.push({
        x: [birthYear, isAlive ? new Date().getFullYear() : deathYear],
        y: [dataPoints.length, dataPoints.length],
        text: [
            `${person.name} - Birth Year`,
            isAlive ? `${person.name} - Still Alive` : `${person.name} - Death Year`
        ],
        type: 'scatter',
        mode: 'lines+markers',
        orientation: 'h',
        line: {
            shape: 'linear',
            width: 4,
        },
        marker: {
            symbol: isAlive ? 'line-ns-open' : 'circle',
            size: 8,
        },
        name: person.name,
    });

    createChart();
}


// Function to show all people on the chart
function showAllAuthors() {

    const dataPoints = [];
    let currentY = 0; // Starting y-coordinate
    const ySpacing = 1; // Vertical spacing between lines

    peopleData.forEach(person => {
        const birthYear = new Date(person.birth_date).getFullYear();
        const deathYear = new Date(person.death_date).getFullYear();

        // Treat authors with death year = 1 as currently alive
        const isAlive = deathYear === 1;

        // Add data points for birth year and death year
        dataPoints.push({
            x: [birthYear, isAlive ? new Date().getFullYear() : deathYear],
            y: [currentY, currentY],
            text: [`${person.name} - Birth Year`, isAlive ? `${person.name} - Still Alive` : `${person.name} - Death Year`],
            type: 'scatter',
            mode: 'lines+markers',
            orientation: 'h',
            line: {
                shape: 'linear',
                width: 2,
            },
            marker: {
                symbol: isAlive ? 'line-ns-open' : 'circle',
                size: 5,
            },
            name: person.name,
        });

        currentY += ySpacing; // Move to the next line for the next person
    });

    // Update the chart with the new data points
    Plotly.newPlot('timespanChart', dataPoints, plotLayout, plotConfig);
}

document.getElementById('showAllButton').addEventListener('click', showAllAuthors);

window.addEventListener("load", (event) => {
  showAllAuthors();
});

document.getElementById('addPersonButton').addEventListener('click', function () {
    const inputBox = document.getElementById('peopleFilter');
    const personName = inputBox.value;

    // Find the person in your data based on the name (replace this with your actual data retrieval logic)
    const person = peopleData.find(p => p.name === personName);

    if (person) {
        addPersonToChart(person);
        inputBox.value = '';
    } else {
        alert('Person not found in the data.');
    }
});