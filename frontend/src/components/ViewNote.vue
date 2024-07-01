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
        <Button v-if="userPermissions.hasPermissionToCreateLink" icon="pi pi-link" @click="showShareLinkPanel"
                severity="help" class="mr-2" label="Поделиться" size="small"></Button>
        <Button v-if="userPermissions.hasPermissionToUpdateNote" @click="goToNoteEditURL" icon="pi pi-pencil"
                severity="warning" class="mr-2" label="Редактировать" size="small"></Button>
        <Button v-if="userPermissions.hasPermissionToDeleteNote" severity="danger" @click="showDeleteModal=true"
                icon="pi pi-trash" label="Удалить" size="small"></Button>
      </div>

    </div>

    <div v-if="note.files.length > 0">
      <div v-if="note.files.length > 0" class="text-sm">
        <i class="pi pi-paperclip"/> Прикрепленные файлы
      </div>
      <ImageGallery :images="noteImages.urls" :with-descriptions="noteImages.names" />
      <div class="mb-2 flex flex-wrap">
        <p v-for="file in noteNonImageFiles" class="mr-3 flex align-items-center">
          <MediaPreview :file="file" :is-file-object="false" :fileNoteID="noteId" :max-file-name-length="20"/>
        </p>
      </div>
    </div>

    <InTextImages v-if="note.content" :text="note.content"/>

    <!-- CONTENT -->
    <NoteContent v-if="note.content" :content="note.content"/>

    <Dialog v-model:visible="showDeleteModal" modal close-icon="pi" header="Подтвердите удаление">
      <div class="flex flex-column align-items-center">
        <div class="font-bold text-red-500">Вы уверены, что хотите удалить данную запись?</div>
        <div class="font-bold text-red-500">Это действие необратимо!</div>
      </div>
      <template #footer>
        <div class="flex align-items-center justify-content-end gap-2">
          <Button label="Нет" severity="primary" autofocus icon="pi pi-angle-left" @click="showDeleteModal = false"/>
          <Button label="Да" severity="danger" icon="pi pi-trash" @click="deleteNote"/>
        </div>
      </template>
    </Dialog>

    <ScrollTop/>

  </div>

  <!--Запись не найдена-->
  <Dialog v-model:visible="noteDoesNotExist" modal :closable="false" :show-header="false" :draggable="false"
          content-class="border-round-md">
    <NoteDoesNotExist/>
  </Dialog>


  <!--Создать временную ссылку-->
  <OverlayPanel ref="shareLink">
    <div class="max-w-20rem">
      <div class="flex flex-wrap gap-2">
        <h4 class="m-0 p-2 mb-2">Создать временную ссылку</h4>
        <InlineMessage severity="info" class="w-full">По данной ссылке любой сможет посмотреть эту запись
        </InlineMessage>
        <InlineMessage severity="warn" class="w-full">Ссылку невозможно будет удалить</InlineMessage>

        <!--Временная ссылка-->
        <div v-if="shareLink" class="w-full p-inputtext link-container">{{ shareLink }}</div>

        <div class="flex w-full align-items-end gap-2 justify-content-end">
          <div class="mt-2">
            <label for="horizontal-buttons" class="block mb-2">Время жизни ссылки</label>
            <InputNumber v-model="shareLinkMinutes" inputId="horizontal-buttons" showButtons buttonLayout="horizontal"
                         :step="1" suffix=" мин." class="justify-content-center" input-class="w-6rem">
              <template #incrementbuttonicon>
                <span class="pi pi-plus"/>
              </template>
              <template #decrementbuttonicon>
                <span class="pi pi-minus"/>
              </template>
            </InputNumber>
          </div>
          <Button @click="getSharedLink" class="w-full justify-content-center">Создать</Button>
        </div>
      </div>
    </div>
  </OverlayPanel>

</template>

<script lang="ts">
import Button from "primevue/button/Button.vue";
import Dialog from "primevue/dialog/Dialog.vue";
import InputNumber from "primevue/inputnumber";
import ScrollTop from "primevue/scrolltop/ScrollTop.vue";
import Toast from "primevue/toast";

import api from "@/services/api";
import {DetailNote, newDetailNote, NoteFile} from "@/note";
import {UserPermissions} from "@/permissions";
import MediaPreview from "./MediaPreview.vue";
import NoteDoesNotExist from "@/components/NoteDoesNotExist.vue";
import {AxiosError, AxiosResponse} from "axios";
import OverlayPanel from "primevue/overlaypanel";
import InTextImages from "@/components/InTextImages.vue";
import ImageGallery from "@/components/ImageGallery.vue";
import NoteContent from "@/components/NoteContent.vue";
import format_bytes from "@/helpers/format_size.ts";

export default {
  name: "ViewNote",
  components: {
    NoteContent,
    ImageGallery,
    InTextImages,
    NoteDoesNotExist,
    Button,
    Dialog,
    InputNumber,
    OverlayPanel,
    MediaPreview,
    ScrollTop,
    Toast,
  },
  props: {
    noteId: {required: true, type: String}
  },
  emits: ["selected-tag"],

  data() {
    return {
      note: null as DetailNote | null,

      shareLinkMinutes: 10,
      shareLink: "",

      noteDoesNotExist: false,

      showDeleteModal: false,
      userPermissions: new UserPermissions([]),
    }
  },

  mounted() {
    api.get("/notes/permissions").then(resp => this.userPermissions = new UserPermissions(resp.data))

    api.get("/notes/" + this.noteId)
        .then(resp => {
          this.note = newDetailNote(resp.data);
          document.title = this.note.title;
        })
        .catch(
            (reason: AxiosError) => {
              if (reason.response?.status === 404) {
                this.noteDoesNotExist = true
              }
            }
        )
  },

  computed: {
    noteImages(): { urls: string[], names: string[] } {
      let imagesUrls: string[] = []
      let imagesNames: string[] = []
      if (this.note?.files) {
        this.note?.files.forEach(file => {
          if (this.isImage(file.name)) {
            imagesUrls.push('/media/' + this.noteId + '/' + file.name)
            imagesNames.push(`<tinytext>${file.name}</tinytext><tinytext>${format_bytes(file.size)}</tinytext>`)
          }
        })
      }
      return {
        urls: imagesUrls,
        names: imagesNames,
      };
    },

    noteNonImageFiles(): NoteFile[] {
      let files: NoteFile[] = []
      this.note?.files.forEach(file => {
        if (!this.isImage(file.name)) files.push(file)
      })
      return files;
    },

  },

  methods: {
    isImage(fileName: string): boolean {
      return RegExp(/.+\.(png|jpe?g|gif|bpm|svg|ico|tiff)$/i).test(fileName)
    },

    goToNoteEditURL(): void {
      window.location.href = "/notes/" + this.noteId + "/edit/"
    },

    deleteNote(): void {
      api.delete("/notes/" + this.noteId)
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
    },

    showShareLinkPanel(event: Event) {
      (<OverlayPanel>this.$refs.shareLink).toggle(event, event.target)
    },

    getSharedLink() {
      const data = {
        minutes: this.shareLinkMinutes
      }
      api.post('/notes/temp/' + this.noteId, data).then(
          (resp: AxiosResponse<{ link: string }>) => {
            this.shareLink = document.location.origin + resp.data.link;
          }
      )
    },

  }
}
</script>


<style scoped>
.link-container {
  user-select: all;
  overflow-x: hidden;
  text-wrap: nowrap;
}
</style>