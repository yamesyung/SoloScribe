console.log(monthlyData);
console.log(pubStats);
console.log(yearStats);
console.log(genreStats);
console.log(genreStatsYear);
console.log(genreCategory);

yearStats.reverse((a, b) => b[2] - a[2]);
authorStats.reverse((a, b) => b[2] - a[2]);

function showTab(tabId) {
    // Hide all tab containers
    document.querySelectorAll('.tab-container').forEach(function (tabContainer) {
        tabContainer.classList.remove('active-tab');
        tabContainer.classList.add('hidden');
    });

    // Show the selected tab container
    const selectedTab = document.getElementById(tabId + '-container');
    selectedTab.classList.add('active-tab');
    selectedTab.classList.remove('hidden');
}

window.onload = function() {
    showTab('author-stats');
}

const colors = ['#e69d87', '#aaaaaa', '#dd6b66'];
let seasonChart = echarts.init(document.getElementById('month-stats'), 'dark');
let scatterChart = echarts.init(document.getElementById('scatter-stats'), 'dark');
let yearChart = echarts.init(document.getElementById('year-stats'), 'dark');
let genreChart = echarts.init(document.getElementById('genre-stats'), 'dark');
let genreChartYear = echarts.init(document.getElementById('genre-stats-year'), 'dark');
let authorChart = echarts.init(document.getElementById('author-stats'), 'dark');
let awardsChart = echarts.init(document.getElementById('awards-stats'), 'dark');
let ratingsChart = echarts.init(document.getElementById('ratings-stats'), 'dark');

let option = {
title: {
    text: "Reading seasons",
    textStyle: {
      fontSize: 30
    },
  },
  color: colors,
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    },
    backgroundColor: '#151b23',
    textStyle: {
      color: '#eeeeee'
    },
  },
  grid: {
    right: '20%'
  },
  legend: {
    data: ['Pages', 'Books', 'Rating']
  },
  xAxis: [
    {
      type: 'category',
      axisTick: {
        alignWithLabel: true
      },
      data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    }
  ],
  yAxis: [
    {
      type: 'value',
      name: 'Pages',
      position: 'right',
      alignTicks: true,
      axisLine: {
        show: true,
        lineStyle: {
          color: colors[0]
        }
      },
      axisLabel: {
        formatter: '{value}'
      }
    },
    {
      type: 'value',
      name: 'Books',
      position: 'right',
      alignTicks: true,
      offset: 80,
      axisLine: {
        show: true,
        lineStyle: {
          color: colors[1]
        }
      },
      axisLabel: {
        formatter: '{value}'
      }
    },
    {
      type: 'value',
      name: 'Rating',
      position: 'left',
      alignTicks: true,
      axisLine: {
        show: true,
        lineStyle: {
          color: colors[2]
        }
      },
      axisLabel: {
        formatter: '{value}'
      }
    }
  ],
  series:[
    {
      name: 'Pages',
      type: 'bar',
      data: monthlyData.map(month => month[2]),
    },
    {
      name: 'Books',
      type: 'bar',
      yAxisIndex: 1,
      data: monthlyData.map(month => month[1]),
    },
    {
      name: 'Rating',
      type: 'line',
      symbol: 'emptyCircle',
      symbolSize: 9,
      lineStyle: {
        width: 4
      },
      yAxisIndex: 2,
      data: monthlyData.map(month => month[3]),
    }
  ]
};

seasonChart.setOption(option);

// Extract the data for label, series, x-axis, and y-axis
var processedData = pubStats.map(function (item) {
return {
  label: item[0],
  series: item[1],
  xAxis: item[2],
  yAxis: item[3]
};
});

var groupedData = {};
processedData.forEach(function (item) {
  if (!groupedData[item.series]) {
    groupedData[item.series] = {
      name: item.series,
      type: 'scatter',
      encode: {
        x: 'xAxis',
        y: 'yAxis',
        tooltip: ['label', 'xAxis', 'yAxis'],
      },
      symbolSize: 10,
      data: []
    };
  }
  groupedData[item.series].data.push({
    label: item.label,
    value: [item.xAxis, item.yAxis]
  });
});

// Create the scatter option
let scatterOption = {
  title: {
    text: 'Publication year',
    textStyle: {
      fontSize: 30
    },
  },
    toolbox: {
    show: true,
    feature: {
      dataZoom: {}
      }},
  xAxis: {
    type: 'time',
    name: 'read in',
    scale: true,
    nameLocation: 'middle',
    nameTextStyle: {
      fontStyle: 'italic',
      fontSize: 14,
    },
    nameGap: 25,
  },
  yAxis: {
    type: 'value',
    name: 'published in',
    scale: true,
    nameLocation: 'middle',
    nameTextStyle: {
      fontStyle: 'italic',
      fontSize: 14,
    },
    nameGap: 40,
  },
  tooltip: {
    trigger: 'item',
    formatter: function (params) {
      var data = params.data || {};
      return (
        '<div>' +
        '<b>' + data.label + '</b><br>' +
        'Read In: ' + data.value[0] + '<br>' +
        'Published In: ' + data.value[1] +
        '</div>'
      );
    },
    backgroundColor: '#151b23',
    textStyle: {
      color: '#eeeeee'
    },
  },
  legend: {
    type: 'scroll',
    orient: 'vertical',
    right: 10,
    top: 55,
    bottom: 20,
    data: Object.keys(groupedData)
  },
  series: Object.values(groupedData)
};

scatterChart.setOption(scatterOption);


let yearOption = {
    title: {
        text: "Reading stats by year",
        textStyle: {
          fontSize: 30
        },
      },
      grid: { containLabel: true},
    tooltip: {
        trigger: 'axis',
        formatter: '{a} <br/>{b}: {c}',
        backgroundColor: '#151b23',
        textStyle: {
         color: '#eeeeee'
        }
    },
    xAxis: [
        {
            type: 'value',
            name: 'Number of Pages',
            nameLocation: 'middle',
            nameTextStyle: {
              fontStyle: 'italic',
              fontSize: 14,
            },
            nameGap: 30,
        },
        {
            type: 'value',
            name: 'Number of Books',
            nameLocation: 'middle',
            nameTextStyle: {
              fontStyle: 'italic',
              fontSize: 14,
            },
            nameGap: 30,
        }
    ],
    yAxis: {
        type: 'category',
        name: 'Year read',
        nameTextStyle: {
            fontWeight: 'bold',
        },
        axisLabel: {
            fontWeight: 'bold',
            fontSize: 14,
        },
        data: yearStats.map(year => year[0]),

    },
    legend: {
        data: ['Number of Pages', 'Number of Books'],
        selected: {
            'Number of Pages': true,  // Initial selection
            'Number of Books': false,
        },
    },
    grid: {
          top: 100, // the size of title + legend + margin
        },
    series: [
        {
            name: 'Number of Pages',
            data: yearStats.map(year => year[2]),
            type: 'bar',
            label: {
                show: true,
                position: 'insideLeft',
                fontWeight: 'bold',
            },
            color: colors[0],
            xAxisIndex: 0, // Use the first x-axis
        },
        {
            name: 'Number of Books',
            data: yearStats.map(year => year[1]),
            type: 'bar',
            label: {
                show: true,
                    position: 'outside',
                    fontWeight: 'bold',
            },
             color: colors[1],
            xAxisIndex: 1, // Use the second x-axis
        }
    ]
};

yearChart.setOption(yearOption);

// Convert the array to an array of objects
const genres = genreStats.map(item => {
  return {
    name: item[0],
    value: item[1]
  };
});

const category = genreCategory.map(item => {
  return {
    name: item[0],
    value: item[1]
  };
});

genreOption = {
  title: {
    text: "Most read genres",
    subtext: 'Top 15, from read bookshelf',
    textStyle: {
      fontSize: 30
    },
  },
  tooltip: {
    trigger: 'item',
    formatter: '<b>{b}</b>: {c} ({d}%)',
    backgroundColor: '#151b23',
    textStyle: {
      color: '#eeeeee'
    },
  },
  series: [
    {
      name: 'Category',
      type: 'pie',
      selectedMode: 'single',
      radius: [0, '30%'],
      label: {
        position: 'inner',
        fontSize: 16,
        fontWeight: 'bold',
        formatter: '{b}: ({d}%)'
      },
      labelLine: {
        show: false
      },
      emphasis: {
        disabled: true
      },
      color: ['#67777e', '#aaaaaa'],
      data: category,
    },
    {
      name: 'Genres',
      type: 'pie',
      radius: ['50%', '75%'],
      labelLine: {
        length: 40
      },
      label: {
        formatter: '{b|{b}：}{c}  {per|{d}%}  ',
        backgroundColor: '#38444d',
        borderColor: 'inherit',
        borderWidth: 3,
        borderRadius: 4,
        rich: {
          b: {
            color: '#f1f2f3',
            fontSize: 14,
            fontWeight: 'bold',
            padding: [3, 4],
            lineHeight: 33
          },
          c: {
            color: '#f1f2f3',
          },
          per: {
            color: '#0a0e0f',
            backgroundColor: '#f2f2f2',
            padding: [3, 4],
            borderRadius: 4
          },

        }
      },
      emphasis: {
          label: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
      data: genres
    }
  ]
};

genreOption && genreChart.setOption(genreOption);


const genreStatsYearPro =  genreStatsYear.map(item => ({
      label: item[0],
      value: item[1],
      series: item[2]
}));


const timelineData = Array.from(new Set(genreStatsYearPro.map(item => item.series)));


const genreStatOption = {
  baseOption: {
    timeline: {
      axisType: 'category',
      playInterval: 5000,
      data: timelineData
    },
    series: [
      {
        name: 'Genre Statistics',
        type: 'pie',
        radius: '50%',
        center: ['50%', '50%'],
        data: [],
        label: {
          show: true,
        },
        labelLine: {
          length: 40
        },
        itemStyle: {
          borderRadius: 5
        },
        animationDuration: 2500,
        animationEasing: "exponentialIn",

        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        }
      }
    ]
  },
  options: timelineData.map(year => ({
    title: {
      text: `Genre Statistics - ${year}`,
      subtext: 'Top 10',
      textStyle: {
        fontSize: 30,
        fontWeight: 'bold'
      },
    },
    series: [
      {
          labelLine: {
          length: 40
        },
          label: {
          show: true, // You might want to show labels
          formatter: '{b|{b}：}{c}  {per|{d}%}  ',
          backgroundColor: '#38444d',
          borderColor: 'inherit',
          borderWidth: 3,
          borderRadius: 4,
          rich: {
            b: {
              color: '#f1f2f3',
              fontSize: 14,
              fontWeight: 'bold',
              padding: [3, 4],
              lineHeight: 33
            },
            c: {
              color: '#f1f2f3',
            },
            per: {
              color: '#0a0e0f',
              backgroundColor: '#f2f2f2',
              padding: [3, 4],
              borderRadius: 4
              }
            }
          },
        data: genreStatsYearPro
          .filter(item => item.series === year)
          .map(item => ({
            name: item.label,
            value: item.value
          }))
      }
    ],

  }))
};

// Set options to the chart
genreChartYear.setOption(genreStatOption);

document.getElementById("genre-stats-year").style.display = "none";

document.addEventListener("change", function(event) {
    if (event.target && event.target.id === "btn-switch") {
        toggleLabel();
    }
});

var authorOption = {
  title: {
    text: "Most read authors",
    subtext: "Top 20 sorted by page count",
    textStyle: {
      fontSize: 30
    },
  },
  grid: { containLabel: true },
  tooltip: {
    trigger: 'axis',
    formatter: '{a} <br/>{b}: {c}',
    backgroundColor: '#151b23',
    textStyle: {
      color: '#eeeeee'
    }
  },
  xAxis: [
    {
      type: 'value',
      name: 'Number of Pages',
      nameLocation: 'middle',
      nameTextStyle: {
        fontStyle: 'italic',
        fontSize: 14,
      },
      nameGap: 30,
    },
    {
      type: 'value',
      name: 'Number of Books',
      nameLocation: 'middle',
      nameTextStyle: {
        fontStyle: 'italic',
        fontSize: 14,
      },
      nameGap: 30,
    }
  ],
  yAxis: {
    type: 'category',
    name: 'Author',
    data: authorStats.map(author => author[0]),
    axisLabel: {
      interval: 0, // Show all labels
    },
  },
  legend: {
    data: ['Number of Pages', 'Number of Books'],
    selected: {
      'Number of Pages': true,  // Initial selection
      'Number of Books': false,
    },
  },
  grid: {
    top: 100, // the size of title + legend + margin
    left: '15%',
  },
  series: [
    {
      name: 'Number of Pages',
      data: authorStats.map(author => author[2]),
      type: 'bar',
      label: {
        show: true,
        position: 'insideLeft',
        fontWeight: 'bold',
      },
      color: colors[0],
      xAxisIndex: 0, // Use the first x-axis
    },
    {
      name: 'Number of Books',
      data: authorStats.map(author => author[1]),
      type: 'bar',
      label: {
        show: true,
        position: 'outside',
        fontWeight: 'bold',
      },
      color: colors[1],
      xAxisIndex: 1, // Use the second x-axis
    }
  ]
};

authorChart.setOption(authorOption);

// Function to convert data to treemap format
function formatToTreemap(data) {
  const treemapData = [];

  // Helper function to find or create a node
  function findOrCreateNode(parent, nodeName) {
    const existingNode = parent.children.find(node => node.name === nodeName);

    if (existingNode) {
      return existingNode;
    }

    const newNode = { name: nodeName, value: 0, children: [] };
    parent.children.push(newNode);
    return newNode;
  }

  // Iterate through the books data and format it for treemap
  for (const book of data) {
    const author = book[0];
    const title = book[1].replace(/&#x27;/g, "'");
    const awards = book[2];
    const bookId = book[3];

    let authorNode = findOrCreateNode({ children: treemapData }, author);
    let titleNode = findOrCreateNode(authorNode, title);

    titleNode.value = awards;
    authorNode.value += awards;

    titleNode.id = bookId;
  }

  return treemapData.sort((a, b) => b.value - a.value);
}

const formattedData = formatToTreemap(awardsData);

const slider = document.getElementById('awards-range-slider');

noUiSlider.create(slider, {
    start: [0, awardsCount],
    connect: true,
    range: {
        'min': 0,
        'max': awardsCount
    },
    step: 1,
    behaviour: 'tap-drag',
    tooltips: [
        {
            to: (value) => Math.round(value),
        },
        {
            to: (value) => Math.round(value),
        }
    ]
});

awardOption = {
  title: {
    text: "Awards stats",
    textStyle: {
      fontSize: 30
    },
  },
  tooltip: {
    formatter: '{b} <br> Awards: {c}',
    backgroundColor: '#151b23',
    textStyle: {
      color: '#eeeeee'
    },
  },
  series: [
    {
      type: 'treemap',
      label: {
        show: true,
        formatter: '{b}',
      },
      upperLabel: {
        show: true,
        height: 18,
      },
      itemStyle: {
        borderColor: '#151b23',
        borderWidth: 1
      },
      data: formattedData.slice(0, awardsCount),
      width: "90%",
      height: "90%",
    }
  ]
};


awardsChart.on('click', function (params) {
    // Extract the data from the clicked node
    const selectedNode = params.data;

    if (selectedNode) {
        // Update the div label with the name of the clicked node
        const divLabelTitle = document.getElementById('awardsDataTitle');
        divLabelTitle.textContent = selectedNode.name;

        const awardsList = document.getElementById('awardsList');
        awardsList.innerHTML = '';

        if (selectedNode.id) {

            fetch(`/books/get-awards-data/${selectedNode.id}/`)
                .then(response => response.json())
                .then(data => {
                    // Update the div label with the fetched data

                    const awardsList = document.getElementById('awardsList');
                    // Clear existing content
                    awardsList.innerHTML = '';

                    // Iterate over each award and create HTML elements
                    data.awards.forEach((award, index) => {
                        const awardElement = document.createElement('span');
                        // Check if awarded_at is null or not
                        if (award.awarded_at) {
                            awardElement.textContent = `${award.name} (${award.awarded_at})`;
                        } else {
                            awardElement.textContent = award.name; // Display only the name
                        }
                        awardsList.appendChild(awardElement);

                        // Insert line break after each span except the last one
                        if (index < data.awards.length - 1) {
                            awardsList.appendChild(document.createElement('br'));
                        }
                    });

                // Update other elements as needed
            })
            .catch(error => console.error('Error fetching data:', error));
        }
    }
});

awardOption && awardsChart.setOption(awardOption);


slider.noUiSlider.on('update', function (values) {
    const fromValue = values[0];
    const toValue = values[1];

    const slicedData = formattedData.slice(fromValue, toValue);
    awardsChart.setOption({
        series: [{
            data: slicedData
        }]
    });
});


//ratings chart
function formatRatingsToTreemap(data) {
  const treemapData = [];


  function findOrCreateNode(parent, nodeName) {
    const existingNode = parent.children.find(node => node.name === nodeName);

    if (existingNode) {
      return existingNode;
    }

    const newNode = { name: nodeName, value: 0, children: [] };
    parent.children.push(newNode);
    return newNode;
  }


  for (const book of data) {
    const author = book[0];
    const title = book[1].replace(/&#x27;/g, "'");
    const ratings = book[2];
    const bookId = book[3];

    let authorNode = findOrCreateNode({ children: treemapData }, author);
    let titleNode = findOrCreateNode(authorNode, title);

    titleNode.value = ratings;
    authorNode.value += ratings;

    titleNode.id = bookId;
  }

  return treemapData.sort((a, b) => b.value - a.value);
}

const formattedRatings = formatRatingsToTreemap(ratingsData);

ratingsOption = {
  title: {
    text: "Book ratings",
    textStyle: {
      fontSize: 30
    },
  },
  tooltip: {
    formatter: '{b} <br> Ratings: {c}',
    backgroundColor: '#151b23',
    textStyle: {
      color: '#eeeeee'
    },
  },
  series: [
    {
      type: 'treemap',
      label: {
        show: true,
        formatter: '{b}',
      },
      upperLabel: {
        show: true,
        height: 18,
      },
      itemStyle: {
        borderColor: '#151b23',
        borderWidth: 1
      },
      data: formattedRatings,
      width: "90%",
      height: "90%",
    }
  ]
};

ratingsOption && ratingsChart.setOption(ratingsOption);
let ratingAuthors = formattedRatings.length;

const ratingsSlider = document.getElementById('ratings-range-slider');

noUiSlider.create(ratingsSlider, {
    start: [0, ratingAuthors],
    connect: true,
    range: {
        'min': 0,
        'max': ratingAuthors
    },
    step: 1,
    behaviour: 'tap-drag',
    tooltips: [
        {
            to: (value) => Math.round(value),
        },
        {
            to: (value) => Math.round(value),
        }
    ]
});

ratingsSlider.noUiSlider.on('update', function (values) {
    const fromValue = values[0];
    const toValue = values[1];

    const slicedData = formattedRatings.slice(fromValue, toValue);
    ratingsChart.setOption({
        series: [{
            data: slicedData
        }]
    });
});


function toggleLabel() {
    var checkbox = document.getElementById("btn-switch");
    var labelText = document.getElementById("labelText");
    var genreStatsDiv = document.getElementById("genre-stats");
    var genreStatsYearDiv = document.getElementById("genre-stats-year");

    if (checkbox.checked) {
        labelText.textContent = "View total";
        genreStatsDiv.style.display = "none";
        genreStatsYearDiv.style.display = "block";
    } else {
        labelText.textContent = "View by year";
        genreStatsDiv.style.display = "block";
        genreStatsYearDiv.style.display = "none";
    }
}

document.addEventListener('DOMContentLoaded', function () {

  var weight = pages * 2;
  var weightKg = pages * 0.002;
  var stackCm = pages * 0.01;
  var stackM = pages * 0.0001;
  var lengthM = pages * 1500 * 0.0025;
  var lengthKm = pages * 1500 * 0.0000025;
  var timeH = pages * 0.0333
  var timeD = pages * 0.00138
  var timeY = pages * 0.0000038

  document.getElementById('pageWeightGrams').innerText = Math.floor(weight);
  document.getElementById('pageWeightKg').innerText = Math.floor(weightKg);
  document.getElementById('heightCm').innerText = Math.floor(stackCm);
  document.getElementById('heightM').innerText = (Math.round(stackM * 100) / 100).toFixed(1);
  document.getElementById('lengthM').innerText = Math.floor(lengthM);
  document.getElementById('lengthKm').innerText = Math.floor(lengthKm);
  document.getElementById('timeH').innerText = Math.floor(timeH);
  document.getElementById('timeD').innerText = Math.floor(timeD);
  document.getElementById('timeY').innerText = (Math.round(timeY * 100) / 100).toFixed(2);
});

window.addEventListener('resize', () => {
    seasonChart.resize();
    scatterChart.resize();
    genreChart.resize();
    genreChartYear.resize();
    awardsChart.resize();
    ratingsChart.resize();
    authorChart.resize();
});