<template>
  <div v-if="noteData" class="surface-section px-4 md:px-6 lg:px-8">

    <Toast/>

    <div class="flex flex-wrap justify-content-between align-items-center">
      <h2 class="border-blue-600 text-2xl p-3 mb-3 text-900" style="border-left: 8px solid;">
        {{ noteData.title }}
      </h2>

      <div class="mb-4">
        <Button @click="goToNoteEditURL" severity="warning" class="mr-2" label="Редактировать" size="small"></Button>
        <Button severity="danger" @click="showDeleteModal=true" label="Удалить" size="small"></Button>
      </div>
    </div>

    <div class="text-600 text-sm mb-3">
      <span class="font-bold"><i class="pi pi-calendar"/> {{ noteData.published_at }}</span>
    </div>


    <!-- TAGS -->
    <div class="mb-5">
      <Tag v-for="tag in noteData.tags" :value="tag"
           class="bg-orange-light hover:bg-indigo-500 hover:shadow-4 mr-2 cursor-pointer font-normal"
           @click="$emit('selected-tag', tag)"/>
    </div>

    <div class="mb-5 flex flex-wrap">
      <p v-for="file in noteData.files" class="mr-3 flex align-items-center">
        <Image v-if="isImage(file.name)"
               :src="getFileDownloadURL(file.name)" :alt="file.name"
               class="mr-2" :image-style="{'max-height': '64px', 'max-width': '64px'}" preview />

        <!-- Иконка формата файла -->
        <img v-else class="mr-2" :src="'/static/'+file.icon" height="48" width="48" :alt="file.name">

        <a :href="getFileDownloadURL(file.name)" class="font-normal no-underline text-900">
          {{ file.name }}<br>
          <span class="text-400" style="font-size: 0.8rem">{{ formatBytes(file.size) }}</span>
        </a>
      </p>
    </div>

    <hr>

    <!-- CONTENT -->
    <div v-html="noteData.content"></div>

    <Dialog v-model:visible="showDeleteModal" modal close-icon="pi" header="Подтвердите удаление" >
      <div class="flex flex-column align-items-center">
        <div class="font-bold text-red-500">Вы уверены, что хотите удалить данную запись?</div>
        <div class="font-bold text-red-500">Это действие необратимо!</div>
      </div>
      <template #footer>
        <div class="flex align-items-center justify-content-end">
          <Button label="Нет" severity="primary" autofocus icon="pi pi-angle-left" @click="showDeleteModal = false" />
          <Button label="Да" severity="danger" icon="pi pi-trash" @click="deleteNote" size="small" />
        </div>
      </template>
    </Dialog>

    <ScrollTop />

  </div>


</template>

<script>
import Button from "primevue/button/Button.vue";
import Dialog from "primevue/dialog/Dialog.vue";
import Image from "primevue/image/Image.vue";
import ScrollTop from "primevue/scrolltop/ScrollTop.vue";
import Tag from "primevue/tag/Tag.vue";
import Toast from "primevue/toast";

import api_request from "../api_request.js";
import format_bytes from "../helpers/format_size.js";

export default {
  name: "ViewNote",
  components: {
    Button,
    Dialog,
    Image,
    ScrollTop,
    Tag,
    Toast,
  },
  props: {
    noteId: {required: true, type: String}
  },
  mounted() {
    api_request.get("/api/notes/"+this.noteId).then(resp => this.noteData = resp.data)
  },
  data() {
    return {
      noteData: null,
      showDeleteModal: false,
    }
  },
  methods: {
    isImage(fileName) {
      return RegExp(/.+\.(png|jpe?g|gif|bpm|svg|ico|tiff)$/i).test(fileName)
    },
    getFileDownloadURL(fileName) {
      return '/api/notes/'+this.noteId+'/files/'+fileName
    },
    formatBytes(size) { return format_bytes(size) },

    goToNoteEditURL() {
      window.location.href = "/notes/" + this.noteId + "/edit/"
    },

    deleteNote() {
      api_request.delete("/api/notes/" + this.noteId)
          .then(resp => window.location.href = "/notes/")
          .catch(
              reason => {
                this.$toast.add({ severity: 'error', summary: 'Error: ' + reason.response.status, detail: reason.response.data, life: 5000 });
              }
          )
      this.showDeleteModal = false
    }
  }
}
</script>

<style scoped>
.bg-orange-light {
  background-color: #FEAA69;
}
</style>