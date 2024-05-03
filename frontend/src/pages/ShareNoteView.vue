<template>
  <div v-if="note" class="p-4">

    <div class="border-blue-600 pl-4 mb-3 text-900" style="border-left: 8px solid;">
      <h1>{{ note.title }}</h1>

      <div class="text-600 text-sm mb-3">
        <span class="font-bold"><i class="pi pi-calendar mr-1"/> {{ note.published_at }}</span>
      </div>

      <!-- TAGS -->
      <div class="mb-5">
        <Tag v-for="tag in note.tags" :value="tag"
             class="bg-orange-light hover:bg-indigo-500 hover:shadow-4 mr-2 cursor-pointer font-normal"
             @click="$emit('selected-tag', tag)"/>
      </div>

    </div>


    <!-- CONTENT -->
    <div v-html="note.content" class="border-300 border-top-1 pt-5"></div>

  </div>

  <!--Запись не найдена-->
  <Dialog v-model:visible="noteLoadError" modal :closable="false" :show-header="false" :draggable="false"
          content-class="border-round-md">
    <NoteDoesNotExist>
      <template #header>
        <span v-if="invalidToken">Временная ссылка неверна</span>
        <span v-if="noteDoesNotExist">Запись не найдена</span>
      </template>
    </NoteDoesNotExist>
  </Dialog>

</template>

<script lang="ts">
import {defineComponent} from 'vue'
import api from "@/services/api.ts";
import {DetailNote, newDetailNote} from "@/note.ts";
import {AxiosError} from "axios";
import NoteDoesNotExist from "@/components/NoteDoesNotExist.vue";

export default defineComponent({
  name: "ShareNoteView",
  components: {NoteDoesNotExist},
  data() {
    return {
      token: this.$route.params.token.toString(),
      note: null as DetailNote | null,

      noteLoadError: false,
      noteDoesNotExist: false,
      invalidToken: false,
    }
  },
  mounted() {

    api.get("/notes/temp/show/" + this.token)
        .then(resp => {
          this.note = newDetailNote(resp.data);
          document.title = this.note.title;
        })
        .catch(
            (reason: AxiosError) => {
              console.log(reason)
              this.noteLoadError = true;
              if (reason.response?.status === 404) {
                this.noteDoesNotExist = true
              } else {
                this.invalidToken = true
              }
            }
        )
  },
})
</script>

<style scoped>

</style>