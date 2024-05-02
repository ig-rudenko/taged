<template>
  <div v-if="note" class="surface-section px-4 md:px-6 lg:px-8">

    <Toast/>

    <div class="flex flex-wrap justify-content-between align-items-center">

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

      <div class="mb-4">
        <Button v-if="userPermissions.hasPermissionToUpdateNote" @click="goToNoteEditURL"
                severity="warning" class="mr-2" label="Редактировать" size="small"></Button>
        <Button v-if="userPermissions.hasPermissionToDeleteNote" severity="danger" @click="showDeleteModal=true"
                label="Удалить" size="small"></Button>
      </div>

    </div>


    <div class="mb-5 flex flex-wrap">
      <p v-for="file in note.files" class="mr-3 flex align-items-center">
        <MediaPreview :file="file" :is-file-object="false" :fileNoteID="noteId"/>
      </p>
    </div>

    <!-- CONTENT -->
    <div v-html="note.content" class="border-300 border-top-1 pt-5"></div>


    <Dialog v-model:visible="showDeleteModal" modal close-icon="pi" header="Подтвердите удаление">
      <div class="flex flex-column align-items-center">
        <div class="font-bold text-red-500">Вы уверены, что хотите удалить данную запись?</div>
        <div class="font-bold text-red-500">Это действие необратимо!</div>
      </div>
      <template #footer>
        <div class="flex align-items-center justify-content-end">
          <Button label="Нет" severity="primary" autofocus icon="pi pi-angle-left" @click="showDeleteModal = false"/>
          <Button label="Да" severity="danger" icon="pi pi-trash" @click="deleteNote" size="small"/>
        </div>
      </template>
    </Dialog>

    <ScrollTop/>

  </div>


</template>

<script lang="ts">
import Button from "primevue/button/Button.vue";
import Dialog from "primevue/dialog/Dialog.vue";
import Image from "primevue/image/Image.vue";
import ScrollTop from "primevue/scrolltop/ScrollTop.vue";
import Tag from "primevue/tag/Tag.vue";
import Toast from "primevue/toast";

import api_request from "../services/api";
import {DetailNote, newDetailNote} from "../note";
import {UserPermissions} from "../permissions";
import MediaPreview from "./MediaPreview.vue";

export default {
  name: "ViewNote",
  components: {
    Button,
    Dialog,
    Image,
    MediaPreview,
    ScrollTop,
    Tag,
    Toast,
  },
  props: {
    noteId: {required: true, type: String}
  },
  mounted() {
    api_request.get("/api/notes/permissions").then(resp => {
      this.userPermissions = new UserPermissions(resp.data)
    })
    api_request.get("/api/notes/" + this.noteId).then(resp => this.note = newDetailNote(resp.data))
  },

  data() {
    return {
      note: null as DetailNote | null,
      showDeleteModal: false,
      userPermissions: new UserPermissions([]),
    }
  },

  methods: {
    isImage(fileName: string): boolean {
      return RegExp(/.+\.(png|jpe?g|gif|bpm|svg|ico|tiff)$/i).test(fileName)
    },

    goToNoteEditURL(): void {
      window.location.href = "/notes/" + this.noteId + "/edit/"
    },

    deleteNote(): void {
      api_request.delete("/api/notes/" + this.noteId)
          .then(() => window.location.href = "/notes/")
          .catch(
              reason => this.$toast.add({
                severity: 'error',
                summary: 'Error: ' + reason.response.status,
                detail: reason.response.data,
                life: 5000
              })
          )
      this.showDeleteModal = false
    }
  }
}
</script>

<style>

@media (max-width: 600px) {
  img {
    width: 100% !important;
    height: 100% !important;
  }
}

.bg-orange-light {
  background-color: #FEAA69;
}
</style>