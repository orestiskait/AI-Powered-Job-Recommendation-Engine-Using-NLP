<template>
  <div class="container">
    <div class="row">
      <div class="offset-lg-3 col-lg-6">
        <div class="input-group mb-3">
          <input type="text" v-model="skill" class="form-control" v-on:keyup.enter="showStats" placeholder="Skill (e.g. Python)" v-focus>
          <div class="input-group-append">
            <button class="btn btn-primary" type="button" id="button-addon2" @click="showStats()">Explore</button>
          </div>
        </div>
      </div>
    </div>

    <div class="row" v-if="loading">
      <Spinner />
    </div>

    <div v-if="!loading && init" class="row ">
      <!-- Bar charts -->
      <div class="col-md-12 text-center">
          <h2>Top Companies</h2>
          <BarChart v-bind:data="data.companies"/>
      </div>
    </div>

     <div v-if="!loading && init" class="row">
      <!-- Bar charts -->
      <div class="col-md-12 text-center">
          <h2>Top Industries</h2>
          <BarChart v-bind:data="data.sectors"/>
      </div>
    </div>

    <div v-if="!loading && init" class="row">
      <!-- Map overview -->

      <div class="col-md-12 text-center">
          <h2>Geographic Demand</h2>
          <MapChart v-bind:data="data.states" class="text-center"/>
      </div>
    </div>

    <div v-if="!loading && init" class="row">
      <!-- Map overview -->

      <div class="col-md-12 text-center">
          <h2>Employers per Industry</h2>
          <BubbleChart v-bind:data="data.bubbles" class="text-center"/>
      </div>
    </div>
  </div>

</template>

<script>
import store from "@store";
import BarChart from "@components/BarChart";
import BubbleChart from "@components/BubbleChart";
import Spinner from "@components/Spinner";
import MapChart from "@components/MapChart";

export default {
  name: "Stats",
  components: {
    BarChart,
    MapChart,
    BubbleChart,
    Spinner
  },
  data: function() {
    return {
      loading: false,
      init: false,
      data: null,
      skill: ""
    };
  },
  directives: {
    focus: {
      inserted: function(el) {
        el.focus();
      }
    }
  },
  methods: {
    showStats() {
      this.loading = true;
      fetch(`${store.apiUrl}/stats?skill=${this.skill}`)
        .then(response => response.json())
        .then(data => {
          this.data = data;

          this.loading = false;
          this.init = true;
        });
    }
  }
};
</script>

<style scoped lang="scss">
</style>
