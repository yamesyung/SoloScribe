console.log(authorData);

var chartDom = document.getElementById('influence-chart');
var influenceChart = echarts.init(chartDom, 'vintage');
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

categories.push({ name: 'Author', itemStyle: { color: '#61a0a8' } });
categories.push({ name: 'Influence', itemStyle: { color: '#d87c7c' } });


option = {
    series: [
        {
            type: 'graph',
            layout: 'force',
            roam: true,
            nodeScaleRatio: 0.7,
            label: {
                show: true,
                color: '#333333',
                position: 'inside',
                fontWeight: 'bold',
            },
            labelLayout: {
                hideOverlap: true,
            },
            symbol: 'circle',
            symbolSize: [20, 6],
            edgeSymbol: ['none', 'arrow'],
            edgeSymbolSize: 15,
            itemStyle: {
                shadowBlur: 10,
            },
            categories: categories,
            data: nodes,
            links: edges,
            selectedMode: "multiple",
            emphasis: {
                scale: 1.4,
                focus: 'adjacency',
                blurScope: 'global',
                itemStyle: {
                    color: '#ffff66',
                },
                lineStyle: {
                    width: 2,
                    color: '#ff5722',
                }
            }
        }
    ]
};

option && influenceChart.setOption(option);

window.addEventListener('resize', () => {
  influenceChart.resize();
});

influenceChart.on('click', function (params) {
    if (params.componentType === 'series' && params.seriesType === 'graph') {
        if (params.dataType === 'node') {
            // Separate edges into outgoing and incoming based on the clicked node
            var outgoingEdges = edges.filter(edge => edge.source === params.data.id);
            var incomingEdges = edges.filter(edge => edge.target === params.data.id);


            // Format outgoing edges
            var outgoingInfo = outgoingEdges.length > 0
                ? outgoingEdges.map(edge => `${edge.target.replace('author_', '')}`).join('<br>')
                : "No data";

            // Format incoming edges
            var incomingInfo = incomingEdges.length > 0
                ? incomingEdges.map(edge => `${edge.source.replace('author_', '')}`).join('<br>')
                : "No data";

            document.getElementById('info-title').innerHTML = `${params.data.name || 'Unnamed'}<br>`;

            document.getElementById('info-list').innerHTML = `
                <strong>Influences:<br></strong><br>
                <span class="author-item">${outgoingInfo}</span><hr>
                <strong>Influenced:<br></strong><br>
                <span class="author-item">${incomingInfo}<hr>`;
        }
    }
});
