console.log(authorData);


var nodes = [];
var edges = [];
var uniqueNodes = new Set();

authorData.forEach(author => {
    var authorNodeId = `author_${author.name}`;
    if (!uniqueNodes.has(authorNodeId)) {
        nodes.push({ id: authorNodeId, label: author.name });
        uniqueNodes.add(authorNodeId);
    }

    author.influences.forEach(influence => {
        var influenceNodeId = `influence_${influence}`;
        if (!uniqueNodes.has(influenceNodeId)) {
            nodes.push({ id: influenceNodeId, label: influence });
            uniqueNodes.add(influenceNodeId);
        }

        edges.push({ from: authorNodeId, to: influenceNodeId, arrows: 'to' });
    });
});

var container = document.getElementById('main');
var data = {
    nodes: nodes,
    edges: edges
};
var options = {};

var network = new vis.Network(container, data, options);