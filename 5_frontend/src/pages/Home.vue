<template>
    <div class="container">
        <div class="row">
            <div class="col-lg-12 text-center">Go ahead, either upload your resume and explore matching jobs or explore the job market for a specific skill.</div>
        </div>
        <div class="row mt-5">
            <div class="col-lg-12 text-center">
                <router-link to="/resume" class="btn btn-primary mr-2">Upload my Resume</router-link>
                <router-link to="/stats" class="btn btn-primary">Explore Skills</router-link>
            </div>
        </div>
    </div>
</template>

<script>
export default {
  name: "Home"
};
</script>

<style scoped lang="scss">
</style>
