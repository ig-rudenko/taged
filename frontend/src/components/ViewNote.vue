<template>
  <div v-if="noteData" class="surface-section px-4 md:px-6 lg:px-8">

    <Toast/>

    <div class="flex flex-wrap justify-content-between align-items-center">

      <div class="border-blue-600 pl-4 mb-3 text-900" style="border-left: 8px solid;">
        <h1>{{ noteData.title }}</h1>

        <div class="text-600 text-sm mb-3">
          <span class="font-bold"><i class="pi pi-calendar mr-1"/> {{ noteData.published_at }}</span>
        </div>

        <!-- TAGS -->
        <div class="mb-5">
          <Tag v-for="tag in noteData.tags" :value="tag"
               class="bg-orange-light hover:bg-indigo-500 hover:shadow-4 mr-2 cursor-pointer font-normal"
               @click="$emit('selected-tag', tag)"/>
        </div>

      </div>

      <div class="mb-4">
        <Button v-if="hasPermissionToUpdateNote" @click="goToNoteEditURL"
                severity="warning" class="mr-2" label="Редактировать" size="small"></Button>
        <Button v-if="hasPermissionToDeleteNote" severity="danger" @click="showDeleteModal=true" label="Удалить" size="small"></Button>
      </div>

    </div>


    <div class="mb-5 flex flex-wrap">
      <p v-for="file in noteData.files" class="mr-3 flex align-items-center">
        <MediaPreview :file="file" :is-file-object="false" :fileNoteID="noteId"/>
      </p>
    </div>

    <!-- CONTENT -->
    <div v-html="noteData.content" class="border-300 border-top-1 pt-5"></div>


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

import MediaPreview from "./MediaPreview.vue";
import api_request from "../api_request.js";
import format_bytes from "../helpers/format_size.js";
import getFileFormatIconName from "../helpers/icons.js";

export default {
  name: "ViewNote",
  components: {
    MediaPreview,
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
    api_request.get("/api/notes/permissions").then(resp => {this.userPermissions = resp.data})

    api_request.get("/api/notes/"+this.noteId).then(resp => this.noteData = resp.data)
  },
  data() {
    return {
      noteData: null,
      showDeleteModal: false,
      userPermissions: [],
    }
  },

  computed: {
    hasPermissionToUpdateNote(){
      return this.userPermissions.includes("update_notes")
    },
    hasPermissionToDeleteNote(){
      return this.userPermissions.includes("delete_notes")
    },
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

    getFileIconURL(fileName) {
      return '/static/images/icons/' + getFileFormatIconName(fileName) + '.png'
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

<style>

@media (max-width: 600px) {
  img {
      width: 100%!important;
      height: 100%!important;
  }
}

.bg-orange-light {
  background-color: #FEAA69;
}
</style>