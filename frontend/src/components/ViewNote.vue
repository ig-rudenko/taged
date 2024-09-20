<template>
  <div v-if="note" class="px-4" :class="noteClasses">

    <div class="flex flex-wrap justify-content-between align-items-center">

      <div class="note-header-block" style="border-left: 8px solid;">
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

      <div class="mb-4 flex flex-wrap gap-2 justify-content-center">
        <Button v-if="userPermissions.hasPermissionToCreateLink" icon="pi pi-link" @click="showShareLinkPanel"
                severity="help" label="Поделиться" size="small"></Button>
        <Button v-if="userPermissions.hasPermissionToUpdateNote" @click="goToNoteEditURL" icon="pi pi-pencil"
                severity="warning" label="Редактировать" size="small"></Button>
        <Button v-if="userPermissions.hasPermissionToDeleteNote" severity="danger" @click="showDeleteModal=true"
                icon="pi pi-trash" label="Удалить" size="small"></Button>
      </div>

    </div>

    <div v-if="note.files.length > 0">
      <div v-if="note.files.length > 0" class="text-sm">
        <i class="pi pi-paperclip"/> Прикрепленные файлы
      </div>
      <ImageGallery :images="noteImages.urls" :with-descriptions="noteImages.names"/>
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
import OverlayPanel from "primevue/overlaypanel";

import {DetailNote, NoteFile} from "@/note";
import {UserPermissions} from "@/permissions";
import MediaPreview from "@/components/MediaPreview.vue";
import NoteDoesNotExist from "@/components/NoteDoesNotExist.vue";
import InTextImages from "@/components/InTextImages.vue";
import ImageGallery from "@/components/ImageGallery.vue";
import NoteContent from "@/components/NoteContent.vue";
import format_bytes from "@/helpers/format_size.ts";
import notesService from "@/services/notes.ts";

export default {
  name: "ViewNote",
  components: {
    NoteContent,
    ImageGallery,
    InTextImages,
    NoteDoesNotExist,
    MediaPreview,
  },
  props: {
    noteId: {required: true, type: String},
    removePadding: {required: false, type: Boolean, default: false},
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
    notesService.getPermissions().then(data => this.userPermissions = new UserPermissions(data))

    notesService.getNote(this.noteId)
        .then(note => {
          this.note = note
          document.title = this.note.title;
        })
  },

  computed: {
    noteClasses(): string[] {
      if (!this.removePadding) return ["lg:px-8"]
      return []
    },

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
      notesService.deleteNote(this.noteId).then(() => window.location.href = "/notes/")
      this.showDeleteModal = false
    },

    showShareLinkPanel(event: Event) {
      (<OverlayPanel>this.$refs.shareLink).toggle(event, event.target)
    },

    async getSharedLink() {
      this.shareLink = await notesService.getTempLink(this.noteId, this.shareLinkMinutes)
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
.note-header-block {
  border-left: 8px solid;
  margin-bottom: 1rem !important;
  padding-left: 1.5rem !important;
  border-color: var(--blue-600) !important;
  color: var(--surface-900) !important;
}

@media (width < 786px) {
  .note-header-block {
    padding-left: 0 !important;
    border-left: 0 solid!important;
    text-align: center;
  }
}
</style>