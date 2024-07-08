<template>
  <div class="surface-section px-4 py-8 md:px-6 lg:px-8">
    <div class="border-top-1 border-300 text-center">
      <ul class="align-items-center flex flex-column justify-content-center lg:flex-row list-none mb-4 mx-0 p-0">
        <li v-if="user && user.isSuperuser">
          <a href="/admin/"
             class="no-underline text-600 cursor-pointer line-height-3 lg:mr-5 gap-2 flex align-items-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-gear"
                 viewBox="0 0 16 16">
              <path
                  d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492M5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0"/>
              <path
                  d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52zm-2.633.283c.246-.835 1.428-.835 1.674 0l.094.319a1.873 1.873 0 0 0 2.693 1.115l.291-.16c.764-.415 1.6.42 1.184 1.185l-.159.292a1.873 1.873 0 0 0 1.116 2.692l.318.094c.835.246.835 1.428 0 1.674l-.319.094a1.873 1.873 0 0 0-1.115 2.693l.16.291c.415.764-.42 1.6-1.185 1.184l-.291-.159a1.873 1.873 0 0 0-2.693 1.116l-.094.318c-.246.835-1.428.835-1.674 0l-.094-.319a1.873 1.873 0 0 0-2.692-1.115l-.292.16c-.764.415-1.6-.42-1.184-1.185l.159-.291A1.873 1.873 0 0 0 1.945 8.93l-.319-.094c-.835-.246-.835-1.428 0-1.674l.319-.094A1.873 1.873 0 0 0 3.06 4.377l-.16-.292c-.415-.764.42-1.6 1.185-1.184l.292.159a1.873 1.873 0 0 0 2.692-1.115z"/>
            </svg>
            <span>Панель администратора</span>
          </a>
        </li>
        <li>
          <span @click="showLogoutDialog=true"
                class="no-underline text-600 cursor-pointer line-height-3 lg:mr-5 flex gap-2 align-items-center">
            <i class="pi pi-sign-out"/>Выйти
          </span>
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
        <p class="mr-5 text-sm text-600">ig-rudenko &copy; 2021-{{ (new Date()).getFullYear() }}</p>
      </div>
    </div>
  </div>

  <Dialog v-model:visible="showLogoutDialog" modal header="Вы уверены, что хотите выйти?">
    <div class="flex justify-content-center gap-2">
      <Button icon="pi pi-times" severity="primary" @click="showLogoutDialog=false" autofocus label="Нет"/>
      <Button icon="pi pi-sign-out" severity="danger" @click="performLogout" outlined label="Выйти"/>
    </div>
  </Dialog>

</template>

<script lang="ts">
import "primeicons/primeicons.css"
import Button from "primevue/button/Button.vue";
import {mapActions, mapState} from "vuex";

export default {
  name: "Footer",
  components: {
    Button,
  },
  data() {
    return {
      showLogoutDialog: false,
    }
  },
  computed: {
    ...mapState({user: (state: any) => state.auth.user}),
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