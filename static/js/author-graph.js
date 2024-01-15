console.log(authorData);

var chartDom = document.getElementById('main');
var myChart = echarts.init(chartDom);
var option;

var nodes = [];
var edges = [];
var categories = [];
var uniqueNodes = new Set();

authorData.forEach(author => {
    var authorNodeId = `author_${author.name}`;
    if (!uniqueNodes.has(authorNodeId)) {
        nodes.push({ id: authorNodeId, name: author.name, category: 0 });
        uniqueNodes.add(authorNodeId);
    }

    author.influences.forEach(influence => {
        var influenceNodeId = `author_${influence}`;
        if (!uniqueNodes.has(influenceNodeId)) {
            nodes.push({ id: influenceNodeId, name: influence, category: 1 });
            uniqueNodes.add(influenceNodeId);
        }

        edges.push({ source: authorNodeId, target: influenceNodeId, category: 0 }); // Assuming all edges belong to the same category for simplicity
    });
});

categories.push({ name: 'Author', itemStyle: { color: '#009688' } });
categories.push({ name: 'Influence', itemStyle: { color: '#ff5722' } });

console.log(nodes);
console.log(edges);
console.log(categories);
console.log(uniqueNodes);

option = {
    series: [
        {
            type: 'graph',
            layout: 'force',
            roam: true,
            label: {
                show: true,
                position: 'inside',
            },
            labelLayout: {
                hideOverlap: true,
            },
            symbol: 'roundRect',
            categories: categories,
            data: nodes,
            links: edges,
            emphasis: {
                focus: 'adjacency',
                blurScope: 'global',
                lineStyle: {
                    color: '#ff5722',
                }
            }
        }
    ]
};

option && myChart.setOption(option);