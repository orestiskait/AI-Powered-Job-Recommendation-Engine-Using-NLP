<template></template>

<script>
import * as d3 from "d3";
import * as d3Tip from "d3-tip";
d3.tip = d3Tip;

export default {
  name: "BubbleChart",
  props: {
    data: Object
  },
  mounted() {
    const tip = d3
      .tip()
      .attr("class", "tooltip")
      .html(function(d) {
        return d.name || "No Industry Provided";
      });

    const colors = ["#E791B3", "#D44E83", "#CE3873", "#C82263", "#C20C53"];

    const w = 1100;
    const h = 800;
    const r = 720;
    const x = d3.scale.linear().range([0, r]);
    const y = d3.scale.linear().range([0, r]);

    let node;
    let root;

    const pack = d3.layout
      .pack()
      .size([r, r])
      .value(function(d) {
        return d.size;
      });
    const vis = d3
      .select(this.$el)
      .insert("svg:svg")
      .attr("width", w)
      .attr("height", h)
      .append("svg:g")
      .attr("transform", "translate(" + (w - r) / 2 + "," + (h - r) / 2 + ")")
      .call(tip);

    node = root = this.data;

    const zScale = d3.scale
      .quantile()
      .domain([root.min, root.max])
      .range(colors);

    const nodes = pack.nodes(root);

    vis
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("svg:circle")
      .attr("class", function(d) {
        return d.children ? "parent" : "child";
      })
      .attr("cx", function(d) {
        return d.x;
      })
      .attr("cy", function(d) {
        return d.y;
      })
      .attr("r", function(d) {
        return d.r;
      })
      .style("fill", function(d) {
        return zScale(d.size) || 0;
      })
      .on("mouseover", tip.show)
      .on("mouseout", tip.hide)
      .on("click", function(d) {
        return zoom(node == d ? root : d);
      });
    vis
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("svg:text")
      .attr("class", function(d) {
        return d.children ? "parent" : "child";
      })
      .attr("x", function(d) {
        return d.x;
      })
      .attr("y", function(d) {
        return d.y;
      })
      .attr("dy", ".35em")
      .attr("text-anchor", "middle")
      .style("opacity", function(d) {
        return d.r > 20 ? 1 : 0;
      })
      .text(function(d) {
        return d.name;
      });
    d3.select(window).on("click", function() {
      zoom(root);
    });

    function zoom(d) {
      var k = r / d.r / 2;
      x.domain([d.x - d.r, d.x + d.r]);
      y.domain([d.y - d.r, d.y + d.r]);
      var t = vis.transition().duration(d3.event.altKey ? 7500 : 750);
      t.selectAll("circle")
        .attr("cx", function(d) {
          return x(d.x);
        })
        .attr("cy", function(d) {
          return y(d.y);
        })
        .attr("r", function(d) {
          return k * d.r;
        });
      t.selectAll("text")
        .attr("x", function(d) {
          return x(d.x);
        })
        .attr("y", function(d) {
          return y(d.y);
        })
        .style("opacity", function(d) {
          return k * d.r > 20 ? 1 : 0;
        });
      node = d;
      d3.event.stopPropagation();
    }
  }
};
</script>

<style lang="scss">
@import "./../assets/theme.scss";

text {
  font-size: 12px;
  pointer-events: none;
  fill: #fff;
}
text.parent {
  display: none;
}
circle {
  fill: $secondary;
  pointer-events: all;
}
circle.parent {
  fill: darken($primary, 30%);
  stroke-width: 2px;
  fill-opacity: 0.1;
  stroke: darken($primary, 10%);
}
circle.parent:hover {
  stroke: $secondary;
  stroke-width: 0.5px;
}
circle.child {
  pointer-events: none;
}
</style>
