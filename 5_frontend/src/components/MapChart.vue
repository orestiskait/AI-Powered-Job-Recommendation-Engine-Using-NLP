<template></template>

<script>
import * as d3 from "d3";
import * as topojson from "topojson";
import * as d3Tip from "d3-tip";
import { idToState, numberWithCommas } from "@helpers";
d3.tip = d3Tip;

export default {
  name: "MapChart",
  props: {
    data: Array
  },
  mounted() {
    const tip = d3
      .tip()
      .attr("class", "tooltip")
      .html(function(d) {
        return (
          "State: \t\t\t\t" +
          d.properties.state +
          "\r\n" +
          "Job Count: \t\t\t" +
          numberWithCommas(d.properties.jobCount)
        );
      });

    const width = 960;
    const height = 600;

    const colors = [
      "#F4BED3",
      "#EDA7C3",
      "#E791B3",
      "#E17BA3",
      "#DB6593",
      "#D44E83",
      "#CE3873",
      "#C82263",
      "#C20C53"
    ];

    const projection = d3.geo
      .albersUsa()
      .precision(0)
      .scale(height * 2)
      .translate([width / 2, height / 2]);

    const path = d3.geo.path().projection(projection);

    const svg = d3
      .select(this.$el)
      .append("svg")
      .attr("width", width)
      .attr("height", height)
      .call(tip);

    fetch("/us_states.json")
      .then(response => response.json())
      .then(topo => {
        const data = this.data.map(state => ({
          state: state.state,
          state_abrev: state.state_abrev,
          jobCount: +state.count,
          jobs: state.jobs
        }));

        const states = topojson.feature(topo, topo.objects.states).features;

        const minJob = d3.min(data, d => d.jobCount);
        const maxJob = d3.max(data, d => d.jobCount);
        const zScale = d3.scale
          .quantile()
          .domain([minJob, maxJob])
          .range(colors);

        const l = Math.floor((maxJob - minJob) / zScale.range().length),
          breaks = d3.range(0, zScale.range().length).map(function(i) {
            return i * l;
          });

        states.forEach(function(f) {
          f.properties = data.find(d => d.state_abrev === idToState[f.id]) || {
            state: idToState[f.id],
            state_abrev: idToState[f.id],
            jobCount: 0,
            jobs: []
          };
        });

        svg
          .selectAll(".state")
          .data(states)
          .enter()
          .append("path")
          .attr("class", "state")
          .attr("d", path)
          .style("fill", d => zScale(d.properties.jobCount))
          .on("mouseover", tip.show)
          .on("mouseout", tip.hide)
          .on("click", d => {
            d3.selectAll(".tooltip").remove();

            this.$emit("show-detail", d.properties.jobs, d.properties.state);
          });

        const w = 18;
        const h = 18;
        const legend = svg
          .selectAll("g.legend")
          .data(breaks)
          .enter()
          .append("g")
          .attr("class", "legend");
        legend
          .append("rect")
          .attr("x", width - 100)
          .attr("y", (d, i) => height - i * h - breaks.length * h)
          .attr("width", w)
          .attr("height", h)
          .style("fill", zScale);
        legend
          .append("text")
          .attr("x", width - 20)
          .attr("y", (d, i) => height - i * h - breaks.length * (h * 0.95))
          .attr("dy", ".35em")
          .style("text-anchor", "end")
          .text(d3.format(String));
      });
  }
};
</script>

<style lang="scss">
@import "../assets/theme.scss";
@import "../../node_modules/bootstrap/scss/_functions";
@import "../../node_modules/bootstrap/scss/_variables";

.state:hover {
  stroke-width: 3;
}

.state {
  cursor: pointer;
  stroke: #333;
  stroke-width: 1;
}

.legend text {
  fill: #fff;
}

.tooltip {
  text-align: left;
  padding: 5px;
  font-size: 12px;
  color: rgb(255, 255, 255);
  background: darken($primary, 20%);
  pointer-events: none;
  white-space: pre-wrap;
}
</style>
