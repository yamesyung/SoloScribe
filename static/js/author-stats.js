console.log(authorStats);
console.log(genresData);

const genresList = Object.entries(genresData).map(([name, value]) => ({ name, value }));
genresList.sort((a, b) => b.value - a.value);
const topGenres = genresList.slice(0, 15);

//weird behavior, although data comes sorted from the query, it need to be reversed when rendering in chart (?)
//add padding in css to remove right label's clipping
authorStats.reverse((a, b) => b[2] - a[2]);
// Initialize the echarts instance based on the prepared dom
var myChart = echarts.init(document.getElementById('author-stats'));
var genreChart = echarts.init(document.getElementById('genres-stats'));


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
                color: '#15a62e',
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
                color: '#ed9d26',
                xAxisIndex: 1, // Use the second x-axis
            }
        ]
};

myChart.setOption(option);

// Add a switch button inside the legend
myChart.on('legendselectchanged', function (params) {
    var selectedSeries = params.selected;
    var newOption = {
        legend: {
            selected: selectedSeries,
        },
    };
    myChart.setOption(newOption);
});


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
      data: topGenres,
    }
  ]
};

optionTwo && genreChart.setOption(optionTwo);