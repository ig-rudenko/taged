<template>
  <Header :section-name="editNoteID?'Редактирование записи':'Создание новой записи'"
          :show-count="false"/>

  <div class="lg:px-8">

    <div class="px-3">
      <Button @click="submit" severity="success" icon="pi pi-check"
              :label="editNoteID?'Обновить':'Создать'"/>
    </div>

    <div class="p-inputgroup p-3">
      <InputText class="text-900" v-model.trim="noteData.title" @update:model-value="() => errors.title=null"
                 style="font-size: 1.5rem; text-align: center"
                 size="lg" placeholder="Укажите заголовок"></InputText>
      <InlineMessage v-if="errors.title">Укажите заголовок</InlineMessage>
    </div>

    <div class="lg:px-8 p-3 flex flex-wrap justify-content-between">
      <div class="lg:border-round p-3">
        <MultiSelect v-model="noteData.tags" @change="() => errors.tags=null"
                     :options="availableTags" filter placeholder="Выберите теги для записи"
                     scroll-height="400px" class="mb-4" />
        <InlineMessage v-if="errors.tags">Выберите хотя бы 1 тег</InlineMessage>
        <div class="px-4 py-2 mb-1 border-round-2xl border-orange-500 border-1 bg-orange-light" v-for="tag in noteData.tags">
          <div class="flex align-items-center">
            <i class="pi pi-tag mr-2" style="font-size: 1.2rem"></i><span>{{tag}}</span>
          </div>
        </div>
      </div>

      <div class="lg:border-round p-3">

        <div v-if="editNoteID" class="align-items-end flex flex-column">
          <div class="font-bold">Существующие файлы</div>
          <div class="flex flex-wrap">
            <div v-for="file in noteData.files" class="p-3 w-15rem">
              <div class="flex align-items-end flex-column">
                <i v-if="file.disable" @click="toggleFile(file)" class="pi pi-check border-round-2xl border-1 px-1 py-1 cursor-pointer hover:text-green-500" aria-label="Cancel" />
                <i v-else @click="toggleFile(file)" class="pi pi-times border-round-2xl border-1 px-1 py-1 cursor-pointer hover:text-red-500" aria-label="Cancel" />
                <div :class="file.disable?['opacity-30']:[]" >
                  <MediaPreview :file="file" :is-file-object="false" :fileNoteID="editNoteID"/>
                </div>
              </div>
            </div>
          </div>
        </div>

        <LoadMedia @selectedFiles="v => updateFiles(v)"/>
      </div>

    </div>

    <div>

      <InlineMessage v-if="errors.content">Укажите содержимое</InlineMessage>
      <ckeditor @click="() => errors.content=null" v-model="noteData.content"
                editor-url="/static/ckeditor/ckeditor/ckeditor.js" value="Hello, World!"></ckeditor>
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

import MediaPreview from "./components/MediaPreview.vue";
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
import api_request from "./api_request.js";
import LoadMedia from "./components/LoadMedia.vue";

export default {
  name: "Notes",
  components: {
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
  },
  data() {
    return {
      files: [],
      noteData: {
        title: "",
        published_at: "",
        tags: [],
        content: "",
        files: [],
      },
      errors: {
        title: null,
        tags: null,
        content: null,
        hasErrors() {
          return this.title && this.tags && this.content
        }
      },
      editNoteID: null,
      availableTags: [],
    }
  },
  mounted() {
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


  methods: {
    getNote() {
      let url = "/api/notes/" + this.editNoteID
      api_request.get(url)
          .then(resp => this.noteData = resp.data)
          .catch(reason => console.log(reason))
    },

    setCkeditorHeight() {
      console.log("setCkeditorHeight", document.getElementById("cke_1_contents"))
      if (document.getElementById("cke_1_contents") === null) {
        setTimeout(this.setCkeditorHeight, 20)
      } else {
        document.getElementById("cke_1_contents").style.height = window.innerHeight + "px"
      }
    },

    updateFiles(files){ this.files = files },

    toggleFile(file) { file.disable = !file.disable },

    /** Подтверждаем данные заметки */
    submit() {
      if (this.noteData.title.length === 0) this.errors.title = true;
      if (this.noteData.tags.length === 0) this.errors.tags = true;
      if (this.noteData.content.length === 0) this.errors.content = true;
      if (this.errors.hasErrors()) return
      let form = new FormData()
      for (const file of this.files) {
        form.append("files", file)
      }

      if (this.editNoteID) {
        // Если заметка уже существовала, то обновляем
        api_request.put("/api/notes/"+this.editNoteID, this.noteData).then(resp => { this.changeFiles(resp.data.id, form) })
      } else {
        // Иначе создаем новую заметку
        api_request.post("/api/notes/", this.noteData).then(resp => { this.changeFiles(resp.data.id, form) })
      }

    },

    /**
     * Обновляем файлы заметки
     * @param {String} note_id
     * @param {FormData} files_form
     */
    changeFiles(note_id, files_form) {
      if (this.editNoteID) {
        // Если заметка редактировалась, то проверяем файлы, которые уже существовали
        for (const file of this.noteData.files) {
          if (file.disable) {
            // Удаляем файлы, которые были отключены
            api_request.delete("/api/notes/" + note_id + '/files/' + file.name)
          }
        }
      }
      // Загружаем новые добавленные файлы
      api_request.post("/api/notes/" + note_id + '/files', files_form)
      this.goToNoteViewURL(note_id)
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