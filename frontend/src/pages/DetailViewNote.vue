<template>
  <Header section-name=""
          :show-count="false"
          :show-create-button="false"/>

  <ViewNote @selected-tag="filterByTag" v-if="noteID" :note-id="noteID"/>

  <Footer/>

</template>

<script lang="ts">
import Header from "@/components/Header.vue";
import ViewNote from "@/components/ViewNote.vue";
import Footer from "@/components/Footer.vue";
import {mapState} from "vuex";

export default {
  name: "DetailViewNote",
  components: {
    Header,
    ViewNote,
    Footer,
  },

  data() {
    return {
      noteID: this.$route.params.id.toString(),
    }
  },

  mounted() {
    if (!this.loggedIn) this.$router.push("/login");
  },

  computed: {
    ...mapState({loggedIn: (state: any) => state.auth.status.loggedIn}),
  },

  methods: {
    filterByTag(tag: string) {
      document.location.href = "/?tags-in=" + tag;
    }
  }

}
</script>

<style scoped>

</style>