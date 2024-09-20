<template>
  <div class="surface-section px-4 py-8 md:px-6 lg:px-8">
    <div class="border-top-1 border-300 text-center">
      <div class="align-items-center flex flex-wrap justify-content-center gap-3 py-3">
        <a v-if="user && user.isSuperuser" href="/admin/" target="_blank"
           class="no-underline text-600 cursor-pointer gap-2 flex align-items-center">
          <i class="pi pi-cog"></i>
          <span>Панель администратора</span>
        </a>
        <div @click="showLogoutDialog=true"
             class="no-underline text-600 cursor-pointer w-10rem align-items-center">
          <i class="pi pi-sign-out mr-2"/>
          <span>Выйти</span>
        </div>
      </div>
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
import {mapActions, mapState} from "vuex";

export default {
  name: "Footer",
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