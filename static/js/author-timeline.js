
console.log(peopleData);
console.log(genreCounts);

const dataPoints = [];

let currentY = 0; // Starting y-coordinate
const ySpacing = 1; // Vertical spacing between lines

peopleData.forEach(person => {
    const birthYear = new Date(person.birth_date).getFullYear();
    const deathYear = new Date(person.death_date).getFullYear();

    // Check if the current person interferes with the previous line
    if (birthYear < currentY) {
        currentY += ySpacing; // Move to the next line
    }

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

const layout = {
    xaxis: {
        title: 'Year',
        type: 'linear',
        tick0: 0,  // Set the initial tick value based on your data
        dtick: 100,   // Set the tick interval based on your data
    },
    yaxis: {
        title: 'Lines',
    },
};

Plotly.newPlot('timespanChart', dataPoints, layout);

// Prepare data for donut chart
const donutChartData = [{
    values: Object.values(genreCounts),
    labels: Object.keys(genreCounts),
    type: 'pie',
    hole: 0.4, // Set the hole size to create a donut chart
}];

// Layout for donut chart
const donutChartLayout = {
    title: 'Genre Count Donut Chart',
};

// Create the donut chart
Plotly.newPlot('donutChart', donutChartData, donutChartLayout);