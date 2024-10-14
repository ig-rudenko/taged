<template>

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
                 size="large" placeholder="Укажите заголовок"/>
    </div>

    <div class="flex flex-column">
      <div class="lg:border-round p-3 flex flex-column">
        <InlineMessage v-if="!note.valid.tags" class="w-fit">Выберите хотя бы 1 тег</InlineMessage>

        <div id="select-tags" class="p-inputgroup flex" style="width: max-content;">
          <MultiSelect v-model="note.tags" display="chip"
                       :options="availableTags" filter placeholder="Выберите теги для записи"
                       scroll-height="400px"/>
          <Button v-if="hasPermissionToCreateTag && !showAddTagInput" @click="showAddTagInput=true"
                  icon="pi pi-plus-circle" severity="warning"/>
          <template v-if="showAddTagInput">
            <InputText class="max-w-11rem" v-model.trim="newTag" @keydown.enter="addNewTag"
                       placeholder="Укажите новый тег"/>
            <Button @click="showAddTagInput=false" icon="pi pi-times" severity="warning"/>
          </template>
        </div>

      </div>

      <div class="lg:border-round p-3">

        <div v-if="editNoteID && note.files.length" class="align-items-end flex flex-column">
          <div class="font-bold">Существующие файлы</div>
          <div class="flex flex-wrap">
            <div v-for="file in note.files" class="p-3">
              <div class="flex align-items-end flex-column h-full">
                <i v-if="file.disable" @click="toggleFile(file)"
                   class="pi pi-check border-round-2xl border-1 px-1 py-1 cursor-pointer hover:text-green-500"
                   aria-label="Cancel"/>
                <i v-else @click="toggleFile(file)"
                   class="pi pi-times border-round-2xl border-1 px-1 py-1 cursor-pointer hover:text-red-500"
                   aria-label="Cancel"/>
                <div :class="file.disable?['opacity-30']:[]" class="align-items-center flex h-full">
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
                :config="ckeditorConfig" editor-url="/ckeditor/ckeditor.js"
                value="Hello, World!"></ckeditor>
    </div>

  </div>

  <Footer/>

</template>

<script>
import {component as ckeditor} from '@mayasabha/ckeditor4-vue3'
import {mapState} from "vuex";

import MediaPreview from "@/components/MediaPreview.vue";
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import LoadMedia from "@/components/LoadMedia.vue";
import {Note} from "@/note";
import notesService from "@/services/notes";
import {CkeditorImages} from "@/services/ckeditor";

export default {
  name: "Notes",
  components: {LoadMedia, Header, Footer, MediaPreview, ckeditor},
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
    if (!this.accessToken) await this.$router.push("/login");

    notesService.getPermissions().then(data => this.userPermissions = data);

    // Проверяем, не является ли данная ссылка редактированием существующей записи
    this.editNoteID = this.$route.params.id
    if (this.editNoteID) {
      // В таком случае получаем её данные
      await this.getNote()
      document.title = "Редактирование: " + this.note.title;
    } else {
      document.title = "Создание записи";
    }

    this.availableTags = await notesService.getAvailableTags();
    this.enableImagesAutoResize();
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
    enableImagesAutoResize() {
      // Если режим редактирования, то пропускаем начальные изображения
      const skipInitialImages = this.editNoteID != null;

      const ckeditorImages = new CkeditorImages(skipInitialImages);
      ckeditorImages.enableImagesAutoSize();
    },

    async getNote() {
      this.note = await notesService.getNote(this.editNoteID);
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

      let filesForm = new FormData()
      for (const file of this.files) {
        filesForm.append("files", file)
      }

      if (this.editNoteID) {
        await notesService.updateNote(this.note, filesForm);
        await this.$router.push("/notes/" + this.editNoteID);
      } else {
        await notesService.createNote(this.note, filesForm);
        await this.$router.push("/notes/");
      }
      this.submitInProcess = false;
    },

  }
}
</script>

<style scoped>
html, body {
  margin: 0 !important;
}

@media (width < 786px) {
  #select-tags {
    width: 100% !important;
  }
}
</style>