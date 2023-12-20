<template>
  <Snow/>
  <Header section-name=""
          :show-count="false"
          :show-create-button="false"/>

  <ViewNote v-if="noteID" :note-id="noteID" />

  <Footer/>

</template>

<script lang="ts">
import Header from "./components/Header.vue";
import ViewNote from "./components/ViewNote.vue";
import Footer from "./components/Footer.vue";
import Snow from "./components/Snow.vue";

export default {
  name: "DetailViewNote",
  components: {
    Snow,
    Header,
    ViewNote,
    Footer,
  },

  data() {
    return {
      noteID: null as string,
    }
  },

  mounted() {
    const match = window.location.href.match(/\/notes\/(\S+)$/);
    if (match) this.noteID = match[1];
  },

}
</script>

<style scoped>

</style>