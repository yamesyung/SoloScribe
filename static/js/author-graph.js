console.log(authorData);


var nodes = [];
var edges = [];
var uniqueNodes = new Set();

authorData.forEach(author => {
    var authorNodeId = `author_${author.name}`;

    // Add the author to nodes only if it doesn't exist
    if (!uniqueNodes.has(authorNodeId)) {
        nodes.push({ id: authorNodeId, label: author.name });
        uniqueNodes.add(authorNodeId);
    }

    author.influences.forEach(influence => {
        var influenceNodeId = `author_${influence}`;

        // Add the influence to nodes only if it doesn't exist
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
var options = {
    interaction: {
        selectConnectedEdges: false // Disable selecting connected edges by default
    }
};

var network = new vis.Network(container, data, options);

// Add event listener for node selection
network.on('selectNode', function (event) {
    var selectedNodeId = event.nodes[0];

    // Reset all node and edge colors
    nodes.forEach(node => {
        node.color = undefined;
    });

    edges.forEach(edge => {
        edge.color = undefined;
    });

    // Highlight the selected node and its connected nodes
    if (selectedNodeId) {
        var selectedNode = nodes.find(node => node.id === selectedNodeId);
        if (selectedNode) {
            selectedNode.color = { background: 'yellow' };
        }

        edges.forEach(edge => {
            if (edge.from === selectedNodeId || edge.to === selectedNodeId) {
                edge.color = { color: 'red' };

                // Highlight connected nodes as well
                var connectedNodeId = edge.from === selectedNodeId ? edge.to : edge.from;
                var connectedNode = nodes.find(node => node.id === connectedNodeId);
                if (connectedNode) {
                    connectedNode.color = { background: 'orange' };
                }
            }
        });
    }

    // Update the network with the new colors
    network.setData({ nodes: nodes, edges: edges });
});