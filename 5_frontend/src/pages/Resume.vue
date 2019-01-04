<template>
  <div>
    <div class="row" v-if="step === 'upload'">
      <div v-show="loading" class="col-md-6 offset-md-3">
        <Spinner />
      </div>
      <div v-show="!loading" class="col-md-6 offset-md-3 content">

        Go ahead, upload your resume and we will find the best jobs for you out of more than 1 million jobs found on the web.

        <vue-dropzone ref="myVueDropzone" id="dropzone"
          :include-styling="false"
          :useCustomSlot="true"
          :options="dropzoneOptions"
          v-on:vdropzone-drop="fileDropped"
          v-on:vdropzone-success="fileSuccess"
          v-on:vdropzone-sending="fileSending">
          <div class="dropzone-custom-content">
            <div class="dropzone-custom-title">Drag and drop a file or click to upload your resume</div>
          </div>
        </vue-dropzone>
      </div>
    </div>
    <div v-if="step === 'map'">
      <h2>Which state are you looking to work in?</h2>

      <MapChart v-bind:data="states" v-on:show-detail="showList" class="text-center"/>
    </div>
    <div class="row" v-else-if="step === 'list'">
      <div class="offset-md-2 col-md-8 ">
        <h2>
        <span class="back" @click="goBack">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M0 0h24v24H0z" fill="none"/><path fill="#FFF" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>
          Back
        </span>
        Your top Jobs in {{selectedState}}</h2>

        <div class="list">
          <div class="list-item" v-for="job in jobs" :key="job.job_id">
            <div class="list-item-title">
              <a v-bind:href="'https://glassdoor.com' + job.apply_url" target="_blank">{{job.job_title}}</a>
            </div>

            <div class="list-item-meta">
              <span>
                <svg class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M0 0h24v24H0z" fill="none"/><path fill="#CCC" d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z"/></svg>
                {{job.employer_name}}
              </span>

              <span>
                <svg class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="#CCC" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/><path d="M0 0h24v24H0z" fill="none"/></svg>
                {{job.location}}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import vue2Dropzone from "vue2-dropzone";
import Spinner from "@components/Spinner";
import MapChart from "@components/MapChart";
import store from "@store";

export default {
  name: "Resume",
  data: function() {
    return {
      dropzoneOptions: {
        url: `${store.apiUrl}/submit-resume`,
        thumbnailWidth: 150,
        maxFilesize: 50,
        method: "post",
        acceptedFiles: "application/pdf"
      },
      loading: false,
      sharedState: store.state,
      step: "upload",
      states: [],
      jobs: [],
      selectedState: null
    };
  },
  components: {
    vueDropzone: vue2Dropzone,
    Spinner,
    MapChart
  },
  methods: {
    fileDropped() {
      // Remove the previously uploaded file to allow the user to upload
      // a fixed file in case the first upload did not work or fit the specs.
      this.$refs.myVueDropzone.removeAllFiles();
    },
    fileSending() {
      // The file is sent to the server, analyzed and the response is the data
      // needed for the visualization and the actually extracted features.
      this.loading = true;
    },
    fileSuccess(file, response) {
      // File was analyzed successfully and we can now show the map with the visualization

      // Save the extracted features to the store in order to use them in the following pages
      store.setFeatures({
        skills: response.skills,
        experience: response.experience,
        degree: response.degree
      });

      this.states = response.states;
      this.step = "map";
    },
    showList(jobs, state) {
      this.jobs = jobs;
      this.selectedState = state;
      this.step = "list";
    },
    goBack() {
      this.step = "map";
    }
  }
};
</script>

<style lang="scss">
@import "../../node_modules/bootstrap/scss/_functions";
@import "../../node_modules/bootstrap/scss/_variables";

.back {
  position: absolute;
  left: 11px;
  top: 10px;
  font-size: 14px;
  cursor: pointer;
}

.list {
  background-color: $gray-100;
  box-shadow: 2px 4px 5px -2px rgba(0, 0, 0, 0.43);
  border-radius: 10px;
  margin-bottom: 5 * $spacer;

  .list-item:last-of-type {
    border: none;
  }

  .list-item {
    padding: 10px;
    border-bottom: solid 1px #eee;

    .list-item-title {
      font-size: 20px;
    }

    .list-item-meta {
      color: #000;
      span {
        margin-right: $spacer * 2;
      }
    }
  }
}

#dropzone {
  margin-top: $spacer;
  height: 300px;
  background: transparent;
  color: #fff;
  border-radius: 15px;
  border-style: dashed;
  border-width: 2px;
  display: flex;
  align-items: center;
  justify-content: center;

  .dz-message,
  .dz-preview {
    z-index: -1;
  }

  &.dz-started .dz-message {
    display: none;
  }

  &.dz-clickable {
    cursor: pointer;
  }

  .dz-preview {
    .dz-success-mark {
      display: none;
    }

    .dz-error-mark {
      display: none;
    }
  }

  &.dz-drag-hover {
    border-color: rgba($color: #fff, $alpha: 0.2);
    transition: border 300ms ease-out;

    .dz-message {
      transition: color 300ms ease-out;
      z-index: -1;
    }
  }
}
</style>

