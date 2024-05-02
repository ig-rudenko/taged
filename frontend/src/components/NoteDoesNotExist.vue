<script lang="ts">
import {defineComponent} from 'vue'

export default defineComponent({
  name: "NoteDoesNotExist",
  methods: {
    goToHomePage() {
      document.location.href = "/"
    }
  }
})
</script>

<template>
  <div class="flex flex-column flex-wrap align-items-center border-round-md">
    <h2>
      <slot name="header">
        Запись не найдена
      </slot>
    </h2>
    <img class="w-30rem mb-2" src="/img/note-not-found.svg" alt="note-error"/>
    <Button severity="help" label="На главную" @click="goToHomePage"></Button>
  </div>
</template>

<style scoped>

</style>