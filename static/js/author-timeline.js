
console.log(peopleData);

// Global layout variable
const globalLayout = {
    autosize: false,
    width: 1200,
    height: 600,
    xaxis: {
        title: 'Year',
        type: 'linear',
        tick0: 0,
        dtick: 25,
    },
    yaxis: {
        title: 'No. of authors',
    },
};

const dataPoints = [];

function createChart() {
         Plotly.newPlot('timespanChart', dataPoints, globalLayout);
}

function clearChart() {
    // Clear the existing data points
    Plotly.purge('timespanChart');
}

function addPersonToChart(person) {


            const birthYear = new Date(person.birth_date).getFullYear();
            const deathYear = new Date(person.death_date).getFullYear();

            // Add data points for birth year and death year
            dataPoints.push({
                x: [birthYear, deathYear],
                y: [dataPoints.length, dataPoints.length],
                text: [`${person.name} - Birth Year`, `${person.name} - Death Year`],
                type: 'scatter',
                mode: 'lines+markers',
                orientation: 'h',
                line: {
                    shape: 'linear',
                    width: 4,
                },
                marker: {
                    symbol: 'circle',
                    size: 8,
                },
                name: person.name,
            });

            // Update the chart
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

        // Add data points for birth year and death year
        dataPoints.push({
            x: [birthYear, deathYear],
            y: [currentY, currentY],
            text: [`${person.name} - Birth Year`, `${person.name} - Death Year`],
            type: 'scatter',
            mode: 'lines+markers',
            orientation: 'h', // Set orientation to horizontal
            line: {
                shape: 'linear',
                width: 2,
            },
            marker: {
                symbol: 'circle',
                size: 5,
            },
            name: person.name,
        });

        currentY += ySpacing; // Move to the next line for the next person
    });

    // Update the chart with the new data points
    Plotly.newPlot('timespanChart', dataPoints, globalLayout);
}

showAllAuthors();
//createChart(peopleData);
document.getElementById('clearChartButton').addEventListener('click', clearChart);
document.getElementById('showAllButton').addEventListener('click', showAllAuthors);

 document.getElementById('addPersonButton').addEventListener('click', function () {
            const inputBox = document.getElementById('peopleFilter');
            const personName = inputBox.value;

            // Find the person in your data based on the name (replace this with your actual data retrieval logic)
            const person = peopleData.find(p => p.name === personName);

            if (person) {
                // Add the person to the chart
                addPersonToChart(person);
                // Clear the input box
                inputBox.value = '';
            } else {
                alert('Person not found in the data.');
            }
        });