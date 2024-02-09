console.log(monthlyData);

const colors = ['#4b565b', '#d7ab82', '#d87c7c'];
var myChart = echarts.init(document.getElementById('month-stats'), 'vintage');

option = {
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
