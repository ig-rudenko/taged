<template>
  <Toast/>

  <Header :section-name="editNoteID?'Редактирование записи':'Создание новой записи'" :show-count="false"/>

  <div class="lg:px-8">

    <div class="px-3">
      <Button v-if="submitInProcess" severity="success" icon="pi pi-spin pi-spinner"
              :label="editNoteID?'Обновляется':'Создается'"/>
      <Button v-else @click="submit" severity="success" icon="pi pi-check" :label="editNoteID?'Обновить':'Создать'"/>
    </div>

    <div class="p-3 flex flex-column">
      <InlineMessage v-if="!note.valid.title" class="w-fit">Укажите заголовок</InlineMessage>
      <InputText class="text-900 w-full" v-model.trim="note.title" style="font-size: 1.5rem; text-align: center"
                 size="lg" placeholder="Укажите заголовок"/>
    </div>

    <div class="flex flex-column">
      <div class="lg:border-round p-3 flex flex-column">
        <InlineMessage v-if="!note.valid.tags" class="w-fit">Выберите хотя бы 1 тег</InlineMessage>

        <div class="p-inputgroup" style="width: max-content">
          <MultiSelect v-model="note.tags" display="chip"
                       :options="availableTags" filter placeholder="Выберите теги для записи"
                       scroll-height="400px"/>
          <Button v-if="hasPermissionToCreateTag && !showAddTagInput" @click="showAddTagInput=true"
                  icon="pi pi-plus-circle" severity="warning"/>
          <template v-if="showAddTagInput">
            <InputText v-model.trim="newTag" @keydown.enter="addNewTag" placeholder="Укажите новый тег"/>
            <Button @click="showAddTagInput=false" icon="pi pi-times" severity="warning"/>
          </template>
        </div>

      </div>

      <div class="lg:border-round p-3">

        <div v-if="editNoteID && note.files.length" class="align-items-end flex flex-column">
          <div class="font-bold">Существующие файлы</div>
          <div class="flex flex-wrap">
            <div v-for="file in note.files" class="p-3 w-15rem">
              <div class="flex align-items-end flex-column">
                <i v-if="file.disable" @click="toggleFile(file)"
                   class="pi pi-check border-round-2xl border-1 px-1 py-1 cursor-pointer hover:text-green-500"
                   aria-label="Cancel"/>
                <i v-else @click="toggleFile(file)"
                   class="pi pi-times border-round-2xl border-1 px-1 py-1 cursor-pointer hover:text-red-500"
                   aria-label="Cancel"/>
                <div :class="file.disable?['opacity-30']:[]">
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
      <ckeditor v-if="accessToken" v-model="note.content"
                :config="ckeditorConfig" editor-url="/static/ckeditor/ckeditor/ckeditor.js"
                value="Hello, World!"></ckeditor>
    </div>

  </div>

  <Footer/>

  <ScrollTop/>

</template>

<script>
import {component as ckeditor} from '@mayasabha/ckeditor4-vue3'
import InputText from "primevue/inputtext/InputText.vue";
import InlineMessage from "primevue/inlinemessage/InlineMessage.vue";
import MultiSelect from "primevue/multiselect/MultiSelect.vue";
import ScrollTop from "primevue/scrolltop/ScrollTop.vue";
import Button from "primevue/button/Button.vue";
import Toast from "primevue/toast";
import {mapState} from "vuex";

import MediaPreview from "@/components/MediaPreview.vue";
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import api from "@/services/api";
import LoadMedia from "@/components/LoadMedia.vue";
import {createNewNote, Note} from "@/note";

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
    Toast,
  },
  data() {
    return {
      files: [],
      note: new Note(),
      availableTags: [],
      userPermissions: [],
      submitInProcess: false,

      showAddTagInput: false,
      editNoteID: null,
      newTag: "",
    }
  },
  async mounted() {
    if (!this.accessToken) this.$router.push("/login");

    api.get("/notes/permissions").then(resp => this.userPermissions = resp.data)

    // Проверяем, не является ли данная ссылка редактированием существующей записи
    this.editNoteID = this.$route.params.id
    if (this.editNoteID) {
      // В таком случае получаем её данные
      await this.getNote()
      document.title = "Редактирование: " + this.note.title;
    } else {
      document.title = "Создание записи";
    }

    // Получаем доступные пользователем теги
    api.get("/notes/tags")
        .then(resp => this.availableTags = resp.data)
        .catch(reason => console.log(reason))
  },

  computed: {
    ...mapState({accessToken: (state) => state.auth.userTokens.accessToken}),
    hasPermissionToCreateTag() {
      return this.userPermissions.includes("add_tags")
    },
    ckeditorConfig() {
      return {
        language: "ru",
        height: '75vh',
        uiColor: "#ffffff",
        filebrowserUploadUrl: "/api/ckeditor/upload/",
        fileTools_requestHeaders: {
          'Authorization': 'Bearer ' + this.accessToken
        },
        iframe_attributes: {
          sandbox: 'allow-scripts allow-same-origin',
          allow: 'autoplay'
        },
        contentsCss: ["/themes/viva-light/theme.css", "/css/styles.min.css", "/css/main.css"],
        bodyClass: "m-4",
        format_pre: {
          element: 'pre',
          attributes: {class: "bg-black-alpha-70 border-round p-3 px-5 shadow-2 text-white w-fit"}
        },
        font_names: 'Cascadia Code, monospace;' +
            'Comic Sans MS/Comic Sans MS, cursive;' +
            'Courier New/Courier New, Courier, monospace;' +
            'Lucida Sans Unicode/Lucida Sans Unicode, Lucida Grande, sans-serif;' +
            'Tahoma/Tahoma, Geneva, sans-serif;' +
            'Times New Roman/Times New Roman, Times, serif;',
        toolbar: [
          {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
          {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
          {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
          // {
          //   'name': 'forms',
          //   'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
          //     'HiddenField']
          // },
          '/',
          {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
          {'name': 'colors', 'items': ['TextColor', 'BGColor']},
          {
            'name': 'basicstyles',
            'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']
          },
          {
            'name': 'paragraph',
            'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
              'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']
          },
          {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
          {
            'name': 'insert',
            'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']
          },
          {'name': 'about', 'items': ['About']},
          '/',
          {
            'name': 'yourcustomtools', 'items': [
              'Maximize',
              'ShowBlocks',
              "RemoveFormat"
            ]
          },
        ]
      }
    }
  },


  methods: {
    getNote() {
      return api.get("/notes/" + this.editNoteID)
          .then(resp => this.note = createNewNote(resp.data))
          .catch(reason => console.log(reason))
    },

    updateFiles(files) {
      this.files = files
    },

    toggleFile(file) {
      file.disable = !file.disable
    },

    addNewTag() {
      if (!this.newTag.length) return;
      this.availableTags.push(this.newTag)
      this.note.tags.push(this.newTag)
      this.newTag = ""
    },

    /** Подтверждаем данные заметки */
    async submit() {
      if (!this.note.isValid() || this.submitInProcess) return;

      this.submitInProcess = true
      let form = new FormData()
      for (const file of this.files) {
        form.append("files", file)
      }

      let resp
      try {
        if (this.editNoteID) {
          // Если заметка уже существовала, то обновляем
          resp = await api.put("/notes/" + this.editNoteID, this.note)
        } else {
          // Иначе создаем новую заметку
          resp = await api.post("/notes/", this.note)
        }
        const data = await resp.data

        if (resp.status === 200 || resp.status === 201) {
          await this.changeFiles(data.id, form)
        } else {
          this.showError(resp.status, data)
        }
      } catch (err) {
        this.showError(err.response.status, err.response.data)
      }
      this.submitInProcess = false

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
            this.handleError(api.delete("/notes/" + note_id + '/files/' + file.name))
          }
        }
      }
      // Загружаем новые добавленные файлы
      const resp = await api.post("/notes/" + note_id + '/files', files_form, {
        headers: {
          "Content-Type": "multipart/form-data",
        }
      })
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
            this.$toast.add({
              severity: 'error',
              summary: 'Error: ' + reason.response.status,
              detail: reason.response.data,
              life: 5000
            });
          }
      )
    },

    /**
     * Выводит ошибку API запроса в toast сообщение
     * @param {Number} status
     * @param {Object} data
     */
    showError(status, data) {
      this.$toast.add({severity: 'error', summary: 'Error: ' + status, detail: data, life: 5000});
    },

    goToNoteViewURL(note_id) {
      this.$router.push("/notes/" + note_id)
    }

  }
}
</script>

<style scoped>
html, body {
  margin: 0 !important;
}
</style>