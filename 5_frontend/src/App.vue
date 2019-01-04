<template>
  <div id="app" class="container-fluid">
    <h1 class="app-title">
      <a href="/#/">CSE6242</a>
    </h1>
    <p class="app-caption">An AI powered job recommendation engine</p>

    <router-view></router-view>
  </div>
</template>

<script>
import store from "./store";

export default {
  name: "app",
  data() {
    return {
      sharedState: store.state
    };
  }
};
</script>

<style lang="scss">
@import "./assets/theme.scss";
@import "../node_modules/bootstrap/scss/_functions";
@import "../node_modules/bootstrap/scss/_variables";
@import "../node_modules/bootstrap/scss/bootstrap.scss";

body {
  background: #4e54c8; /* fallback for old browsers */
  background: -webkit-linear-gradient(
    to right,
    #8f94fb,
    #4e54c8
  ); /* Chrome 10-25, Safari 5.1-6 */
  background: linear-gradient(
    to right,
    #8f94fb,
    #4e54c8
  ); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */
  color: #fff;
}

a {
  color: $secondary;
}

h1,
h2,
h3,
h4,
h5 {
  font-family: "Montserrat", sans-serif;
  text-align: center;
}

.app-title {
  font-family: "Montserrat", sans-serif;
  font-size: 42px;
  text-align: center;

  a {
    color: #3f427c;
    text-decoration: none;
  }
}

.app-caption {
  font-family: "Montserrat", sans-serif;
  font-size: 20px;
  text-align: center;
}

#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  margin-top: $spacer * 2;
}
</style>
