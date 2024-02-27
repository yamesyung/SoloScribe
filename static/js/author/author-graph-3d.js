console.log(authorData);

const myGraph = ForceGraph3D()
    (document.getElementById('3d-graph'))
        .graphData(authorData);

        /*
        .nodeThreeObject(node => {
          const sprite = new SpriteText(node.name);
          sprite.material.depthWrite = false;
          sprite.color = 'white';
          sprite.textHeight = 8;
          return sprite;
        });
        */
