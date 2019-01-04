<template></template>

<script>
import * as d3 from "d3";
import { numberWithCommas } from "@helpers";

export default {
  name: "Stats",
  props: {
    data: Array
  },
  data() {
    const margin = { top: 20, right: 0, bottom: 150, left: 50 };
    const width = 900 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;
    const padding = 20;

    return {
      size: { margin, width, height, padding }
    };
  },
  mounted() {
    this.svg = d3
      .select(this.$el)
      .append("svg")
      .attr(
        "width",
        this.size.width + this.size.margin.left + this.size.margin.right
      )
      .attr(
        "height",
        this.size.height + this.size.margin.top + this.size.margin.bottom
      )
      .append("g")
      .attr(
        "transform",
        "translate(" + this.size.margin.left + "," + this.size.margin.top + ")"
      );

    const xScale = d3.scale
      .ordinal()
      .domain(this.data.map(d => d.name))
      .rangeBands([this.size.padding, this.size.width - this.size.padding * 2]);
    const xAxis = d3.svg
      .axis()
      .scale(xScale)
      .orient("bottom");
    this.svg
      .append("g")
      .attr("class", "axis")
      .attr(
        "transform",
        "translate(" + 0 + "," + (this.size.height - this.size.padding) + ")"
      )
      .call(xAxis)
      .selectAll(".tick text")
      .attr("y", 0)
      .attr("x", 9)
      .attr("dy", ".35em")
      .attr("transform", "rotate(90)")
      .style("text-anchor", "start");

    const maxY = d3.max(this.data, d => d["value"]);

    const yScale = d3.scale
      .linear()
      .domain([0, maxY])
      .range([this.size.height - this.size.padding, this.size.padding]);
    const yAxis = d3.svg
      .axis()
      .scale(yScale)
      .orient("left");
    this.svg
      .append("g")
      .attr("class", "axis")
      .attr("transform", "translate(" + this.size.padding + "," + 0 + ")")
      .call(yAxis)
      .append("text")
      .attr("class", "label")
      .attr("transform", "rotate(-90)")
      .attr("y", 0)
      .attr("x", -this.size.height / 2.1)
      .attr("dy", "-" + this.size.padding * 3)
      .style("text-anchor", "end")
      .text("Number of Jobs");

    const bars = this.svg
      .selectAll(".bar")
      .data(this.data)
      .enter()
      .append("g")
      .attr("class", "bar");
    bars
      .append("rect")
      .attr("x", d => xScale(d.name) + this.size.padding / 2)
      .attr("y", d => yScale(d.value))
      .attr("height", d => yScale(0) - yScale(d.value))
      .attr("width", xScale.rangeBand() - this.size.padding);

    bars
      .append("text")
      .attr("y", d => yScale(d.value))
      .attr(
        "x",
        d => xScale(d.name) + xScale.rangeBand() / 2 - this.size.padding / 2
      )
      .text(d => numberWithCommas(d.value));
  }
};
</script>

<style lang="scss">
.axis {
  font: 12px sans-serif;
  fill: #4e54c8;
}
.axis path,
.axis line {
  fill: none;
  stroke: #4e54c8;
  shape-rendering: crispEdges;
  stroke-width: 1px;
}

.bar rect {
  fill: #c51b8a;
}

.bar text {
  fill: #4e54c8;
  font-weight: bold;
}
</style>
