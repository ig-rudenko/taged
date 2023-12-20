<template>
  <Snow/>
  <Header :section-name="editNoteID?'Редактирование записи':'Создание новой записи'"
          :show-count="false"/>

  <Toast />

  <div class="lg:px-8">

    <div class="px-3">
      <Button @click="submit" severity="success" icon="pi pi-check"
              :label="editNoteID?'Обновить':'Создать'"/>
    </div>

    <div class="p-inputgroup p-3">
      <InputText class="text-900" v-model.trim="note.title"
                 style="font-size: 1.5rem; text-align: center"
                 size="lg" placeholder="Укажите заголовок"></InputText>
      <InlineMessage v-if="!note.valid.title">Укажите заголовок</InlineMessage>
    </div>

    <div class="flex flex-column">
      <div class="lg:border-round p-3 flex align-items-center">
        <div class="p-inputgroup" style="width: max-content">
          <MultiSelect v-model="note.tags" display="chip"
                       :options="availableTags" filter placeholder="Выберите теги для записи"
                       scroll-height="400px"/>
          <Button v-if="hasPermissionToCreateTag && !showAddTagInput"
                  @click="showAddTagInput=true" icon="pi pi-plus-circle" severity="warning" />
          <template v-if="showAddTagInput">
            <InputText v-model.trim="newTag" @keydown.enter="addNewTag" placeholder="Укажите новый тег" />
            <Button @click="showAddTagInput=false" icon="pi pi-times" severity="warning" />
          </template>
        </div>

        <InlineMessage v-if="!note.valid.tags">Выберите хотя бы 1 тег</InlineMessage>

      </div>

      <div class="lg:border-round p-3">

        <div v-if="editNoteID && note.files.length" class="align-items-end flex flex-column">
          <div class="font-bold">Существующие файлы</div>
          <div class="flex flex-wrap">
            <div v-for="file in note.files" class="p-3 w-15rem">
              <div class="flex align-items-end flex-column">
                <i v-if="file.disable" @click="toggleFile(file)" class="pi pi-check border-round-2xl border-1 px-1 py-1 cursor-pointer hover:text-green-500" aria-label="Cancel" />
                <i v-else @click="toggleFile(file)" class="pi pi-times border-round-2xl border-1 px-1 py-1 cursor-pointer hover:text-red-500" aria-label="Cancel" />
                <div :class="file.disable?['opacity-30']:[]" >
                  <MediaPreview :file="file" :is-file-object="false"
                                :max-file-name-length="20" :fileNoteID="editNoteID"/>
                </div>
              </div>
            </div>
          </div>
        </div>

        <LoadMedia @selectedFiles="v => updateFiles(v)"/>
      </div>

    </div>

    <div>

      <InlineMessage v-if="!note.valid.content">Укажите содержимое</InlineMessage>
      <ckeditor v-model="note.content" editor-url="/static/ckeditor/ckeditor/ckeditor.js" value="Hello, World!"></ckeditor>
    </div>

  </div>

  <Footer/>

  <ScrollTop />

</template>

<script>
import { component as ckeditor } from '@mayasabha/ckeditor4-vue3'
import InputText from "primevue/inputtext/InputText.vue";
import InlineMessage from "primevue/inlinemessage/InlineMessage.vue";
import MultiSelect from "primevue/multiselect/MultiSelect.vue";
import ScrollTop from "primevue/scrolltop/ScrollTop.vue";
import Button from "primevue/button/Button.vue";
import Toast from "primevue/toast";

import MediaPreview from "./components/MediaPreview.vue";
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
import api_request from "./api_request.ts";
import LoadMedia from "./components/LoadMedia.vue";
import {createNewNote, Note} from "./note.ts";
import Snow from "./components/Snow.vue";

export default {
  name: "Notes",
  components: {
    Snow,
    LoadMedia,
    InlineMessage,
    Header,
    Button,
    Footer,
    InputText,
    MediaPreview,
    MultiSelect,
    ckeditor,
    ScrollTop,
    Toast,
  },
  data() {
    return {
      files: [],
      note: new Note(),
      availableTags: [],
      userPermissions: [],

      showAddTagInput: false,
      editNoteID: null,
      newTag: "",
    }
  },
  mounted() {
    api_request.get("/api/notes/permissions").then(resp => {this.userPermissions = resp.data})

    // Проверяем, не является ли данная ссылка редактированием существующей записи
    const match = window.location.href.match(/notes\/(\S+)\/edit\/$/)
    if (match) {
      // В таком случае получаем её данные
      this.editNoteID = match[1]
      this.getNote()
    }

    // Получаем доступные пользователем теги
    api_request.get("/api/notes/tags")
        .then(resp => this.availableTags = resp.data)
        .catch(reason => console.log(reason))

    this.setCkeditorHeight() // Изменяем высоту окна ckeditor
  },


  computed: {
    hasPermissionToCreateTag() {
      return this.userPermissions.includes("add_tags")
    },
  },


  methods: {
    getNote() {
      let url = "/api/notes/" + this.editNoteID
      api_request.get(url)
          .then(resp => this.note = createNewNote(resp.data))
          .catch(reason => console.log(reason))
    },

    setCkeditorHeight() {
      if (document.getElementById("cke_1_contents") === null) {
        setTimeout(this.setCkeditorHeight, 20)
      } else {
        document.getElementById("cke_1_contents").style.height = window.innerHeight + "px"
      }
    },

    updateFiles(files){ this.files = files },

    toggleFile(file) { file.disable = !file.disable },

    addNewTag() {
      console.log(this.newTag)
      if (!this.newTag.length) return;
      this.availableTags.push(this.newTag)
      this.note.tags.push(this.newTag)
      this.newTag = ""
    },

    /** Подтверждаем данные заметки */
    async submit() {
      if (!this.note.isValid()){ return }

      let form = new FormData()
      for (const file of this.files) {
        form.append("files", file)
      }

      let resp
      if (this.editNoteID) {
        // Если заметка уже существовала, то обновляем
        resp = await api_request.put("/api/notes/"+this.editNoteID, this.note)
      } else {
        // Иначе создаем новую заметку
        resp = await api_request.post("/api/notes/", this.note)
      }
      const data = await resp.data

      if (resp.status === 200 || resp.status === 201){
        await this.changeFiles(data.id, form)
      } else {
        this.showError(resp.status, data)
      }

    },

    /**
     * Обновляем файлы заметки
     * @param {String} note_id
     * @param {FormData} files_form
     */
    async changeFiles(note_id, files_form) {
      if (this.editNoteID) {
        // Если заметка редактировалась, то проверяем файлы, которые уже существовали
        for (const file of this.note.files) {
          if (file.disable) {
            // Удаляем файлы, которые были отключены
            this.handleError(api_request.delete("/api/notes/" + note_id + '/files/' + file.name))
          }
        }
      }
      // Загружаем новые добавленные файлы
      const resp = await api_request.post("/api/notes/" + note_id + '/files', files_form)
      const data = await resp.data

      if (resp.status === 201) {
        this.goToNoteViewURL(note_id)
      } else {
        this.showError(resp.status, data)
      }
    },

    /**
     * Обрабатывает ошибку API запроса и выводит в toast сообщение
     * @param {Promise} request
     */
    handleError(request) {
      request.catch(
          reason => {
            this.$toast.add({ severity: 'error', summary: 'Error: ' + reason.response.status, detail: reason.response.data, life: 5000 });
          }
      )
    },

    /**
     * Выводит ошибку API запроса в toast сообщение
     * @param {Number} status
     * @param {Object} data
     */
    showError(status, data) {
      this.$toast.add({ severity: 'error', summary: 'Error: ' + status, detail: data, life: 5000 });
    },

    goToNoteViewURL(note_id) {
      window.location.href = "/notes/" + note_id
    }

  }
}
</script>

<style scoped>
html, body {
  margin: 0!important;
}

@media (max-height > 100px) {
  .cke_1_contents {
    //height: 500px!important;
  }
}

.bg-orange-light {
  background-color: #FEAA69;
}

.bg-purple-light {
  background-color: #bd77ff;
}

.total-match {
  box-shadow: 0 4px 10px #bd77ffaa,0 0 2px #bd77ffaa,0 2px 6px #bd77ff33!important;
}
</style>