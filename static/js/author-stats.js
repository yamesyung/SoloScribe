console.log(authorStats);
console.log(genresData);
console.log(awardsData);
console.log(pages);


const genresList = Object.entries(genresData).map(([name, value]) => ({ name, value }));
genresList.sort((a, b) => b.value - a.value);

//weird behavior, although data comes sorted from the query, it need to be reversed when rendering in chart (?)
//add padding in css to remove right label's clipping
authorStats.reverse((a, b) => b[2] - a[2]);
// Initialize the echarts instance based on the prepared dom
var myChart = echarts.init(document.getElementById('author-stats'), 'vintage');
var genreChart = echarts.init(document.getElementById('genres-stats'), 'vintage');
var awardsChart = echarts.init(document.getElementById('awards-stats'), 'vintage');


var option = {
        title: {
            text: "Most read authors",
            subtext: "Top 20 sorted by page count",
            textStyle: {
              fontSize: 30
            },
          },
          grid: { containLabel: true},
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c}'
        },
        xAxis: [
            {
                type: 'value',
                name: 'Number of Pages',
            },
            {
                type: 'value',
                name: 'Number of Books',
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
            },
        series: [
            {
                name: 'Number of Pages',
                data: authorStats.map(author => author[2]),
                type: 'bar',
                label: {
                    show: true,
                    position: 'insideRight', // Show labels inside the bar
                },
                color: '#d7ab82',
                xAxisIndex: 0, // Use the first x-axis
            },
            {
                name: 'Number of Books',
                data: authorStats.map(author => author[1]),
                type: 'bar',
                label: {
                    show: true,
                    position: 'insideRight', // Show labels inside the bar
                },
                 color: '#4b565b',
                xAxisIndex: 1, // Use the second x-axis
            }
        ]
};

myChart.setOption(option);


optionTwo = {
  tooltip: {
    trigger: 'item'
  },
  title: {
    text: "Most popular genres",
    subtext: "Top 15, data is from author's Goodreads page",
    textStyle: {
      fontSize: 30
    },
  },
  legend: {
    type: 'scroll',
    orient: 'vertical',
    right: 10,
    top: 20,
    bottom: 20,
  },
  series: [
    {
      name: 'Genre',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 30,
          fontWeight: 'bold'
        },
        scale: true,
        scaleSize: 16
      },
      labelLine: {
        show: false
      },
      data: genresList.slice(0, 15),
    }
  ]
};

optionTwo && genreChart.setOption(optionTwo);


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
    const title = book[1];
    const awards = book[2];

    let authorNode = findOrCreateNode({ children: treemapData }, author);
    let titleNode = findOrCreateNode(authorNode, title);

    titleNode.value = awards;
    authorNode.value += awards;
  }

  return treemapData.sort((a, b) => b.value - a.value);
}

const formattedData = formatToTreemap(awardsData);

optionTree = {
    title: {
        text: "Most awarded authors",
        textStyle: {
          fontSize: 30
        },
      },
    tooltip: {
        formatter: '{b} <br> Awards: {c}'
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
            borderColor: '#fff',
            borderWidth: 1
          },
      data: formattedData.slice(0, 30),
      width: "90%",
      height: "90%",
    }
  ]
};

optionTree && awardsChart.setOption(optionTree);


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
    document.getElementById('heightM').innerText = Math.floor(stackM);
    document.getElementById('lengthM').innerText = Math.floor(lengthM);
    document.getElementById('lengthKm').innerText = Math.floor(lengthKm);
    document.getElementById('timeH').innerText = Math.floor(timeH);
    document.getElementById('timeD').innerText = Math.floor(timeD);
    document.getElementById('timeY').innerText = (Math.round(timeY * 100) / 100).toFixed(2);
});

function showTab(tabId) {
// Hide all tabs
    var tabs = document.getElementsByClassName('tab');
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].style.display = 'none';

    }

    // Show the selected tab
    document.getElementById(tabId).style.display = 'block';

    if (tabId === 'author-stats') {
        document.querySelector('.facts').style.display = 'block';
    } else {
        // Hide the 'Fun fact' div for other tabs
        document.querySelector('.facts').style.display = 'none';
    }
}

window.onload = function() {
    showTab('author-stats');
};

function controlFromSlider(fromSlider, toSlider) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, '#C6C6C6', '#25daa5', toSlider);
  if (from > to) {
    fromSlider.value = to;
  }
}

function controlToSlider(fromSlider, toSlider) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, '#C6C6C6', '#25daa5', toSlider);
  setToggleAccessible(toSlider);
  if (from <= to) {
    toSlider.value = to;
  } else {
    toSlider.value = from;
  }
}

function getParsed(currentFrom, currentTo) {
  const from = parseInt(currentFrom.value, 10);
  const to = parseInt(currentTo.value, 10);
  return [from, to];
}

function fillSlider(from, to, sliderColor, rangeColor, controlSlider) {
    const rangeDistance = to.max-to.min;
    const fromPosition = from.value - to.min;
    const toPosition = to.value - to.min;
    controlSlider.style.background = `linear-gradient(
      to right,
      ${sliderColor} 0%,
      ${sliderColor} ${(fromPosition)/(rangeDistance)*100}%,
      ${rangeColor} ${((fromPosition)/(rangeDistance))*100}%,
      ${rangeColor} ${(toPosition)/(rangeDistance)*100}%,
      ${sliderColor} ${(toPosition)/(rangeDistance)*100}%,
      ${sliderColor} 100%)`;
}

function setToggleAccessible(currentTarget) {
  const toSlider = document.querySelector('#toSlider');
  if (Number(currentTarget.value) <= 0 ) {
    toSlider.style.zIndex = 2;
  } else {
    toSlider.style.zIndex = 0;
  }
}

const fromSlider = document.querySelector('#fromSlider');
const toSlider = document.querySelector('#toSlider');
fillSlider(fromSlider, toSlider, '#C6C6C6', '#25daa5', toSlider);
setToggleAccessible(toSlider);

fromSlider.oninput = () => controlFromSlider(fromSlider, toSlider);
toSlider.oninput = () => controlToSlider(fromSlider, toSlider);

var minText = document.getElementById("valueMin");
var maxText = document.getElementById("valueMax");

minText.innerHTML = fromSlider.value;
maxText.innerHTML = toSlider.value;

toSlider.max = formattedData.length;

toSlider.oninput = function() {
  maxText.innerHTML = this.value;
  var slicedData = formattedData.slice(fromSlider.value, this.value);

    awardsChart.setOption({
    series: [
      {
        data: slicedData,
      },
    ]
  });
}

fromSlider.oninput = function() {
  minText.innerHTML = this.value;
  var slicedData = formattedData.slice(this.value, toSlider.value);

    awardsChart.setOption({
    series: [
      {
        data: slicedData,
      },
    ]
  });
}


