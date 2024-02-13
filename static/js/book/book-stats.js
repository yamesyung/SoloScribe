console.log(monthlyData);
console.log(pubStats);
console.log(yearStats);
console.log(genreStats);
console.log(genreCategory);

yearStats.reverse((a, b) => b[2] - a[2]);

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
    showTab('season-stats')
}

const colors = ['#4b565b', '#d7ab82', '#d87c7c'];
let myChart = echarts.init(document.getElementById('month-stats'), 'vintage');
let scatterChart = echarts.init(document.getElementById('scatter-stats'), 'vintage');
let yearChart = echarts.init(document.getElementById('year-stats'), 'vintage');
let genreChart = echarts.init(document.getElementById('genre-stats'), 'vintage');

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
    }
  },
  grid: {
    right: '20%'
  },
  legend: {
    data: ['Books', 'Pages', 'Rating']
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
      name: 'Books',
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
      name: 'Pages',
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
      name: 'Books',
      type: 'bar',
      data: monthlyData.map(month => month[1]),
    },
    {
      name: 'Pages',
      type: 'bar',
      yAxisIndex: 1,
      data: monthlyData.map(month => month[2]),
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

myChart.setOption(option);

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
    nameLocation: 'middle',
    nameTextStyle: {
      fontStyle: 'italic',
      fontSize: 14,
    },
    nameGap: 40,
    max: 2500,
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
    }
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
        formatter: '{a} <br/>{b}: {c}'
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
            color: '#d7ab82',
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
             color: '#4b565b',
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
    formatter: '<b>{b}</b>: {c} ({d}%)'
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
      color: ['#67777e', '#aaaaaa'],
      data: category,
    },
    {
      name: 'Genres',
      type: 'pie',
      radius: ['45%', '60%'],
      labelLine: {
        length: 30
      },
      label: {
        formatter: '{b|{b}：}{c}  {per|{d}%}  ',
        backgroundColor: '#F6F8FC',
        borderColor: '#8C8D8E',
        borderWidth: 1,
        borderRadius: 4,
        rich: {
          b: {
            color: '#4C5058',
            fontSize: 14,
            fontWeight: 'bold',
            lineHeight: 33
          },
          per: {
            color: '#fff',
            backgroundColor: '#4C5058',
            padding: [3, 4],
            borderRadius: 4
          }
        }
      },
      data: genres
    }
  ]
};

genreOption && genreChart.setOption(genreOption);
