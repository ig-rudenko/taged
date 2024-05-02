<template>
  <div class="surface-section px-4 py-8 md:px-6 lg:px-8">
    <div class="border-top-1 border-300 text-center">
      <ul class="align-items-center flex flex-column justify-content-center lg:flex-row list-none mb-4 mx-0 p-0">
        <li v-if="showLogout">
          <span class="no-underline text-600 cursor-pointer line-height-3 lg:mr-5" @click="performLogout">Выйти</span>
        </li>
      </ul>
      <div class="flex align-items-center justify-content-center mb-5">
        <a href="https://github.com/ig-rudenko/taged"
           class="pi pi-github no-underline text-black-alpha-80 mr-5 block inline-flex justify-content-center align-items-center"
           style="font-size: 2.5rem;"></a>
        <a href="https://www.elastic.co/elasticsearch/" target="_blank" title="Elasticsearch"
           class="no-underline text-black-alpha-80 mr-5 block inline-flex justify-content-center align-items-center">
          <img src="/icons/elasticsearch.svg" alt="elasticsearch" style="width: 2.5rem; height: 2.5rem"/>
        </a>
      </div>
      <div class="text-center">
        <p class="mr-5 text-sm text-600 cursor-pointer">ig-rudenko &copy; 2021-{{ (new Date()).getFullYear() }}</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import "primeicons/primeicons.css"
import Button from "primevue/button/Button.vue";
import {mapActions} from "vuex";

export default {
  name: "Footer",
  components: {
    Button,
  },
  props: {
    showLogout: {required: false, type: Boolean, default: true},
  },
  methods: {
    ...mapActions("auth", ["logout"]),
    performLogout() {
      this.logout()
      this.$router.push("/login")
    },
  }
}

</script>

<style scoped>

</style>