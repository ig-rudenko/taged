<template>
  <Header section-name="Создание новой записи" :show-count="false"/>

  <div class="lg:px-8">

    <div class="px-3">
      <Button @click="submit" severity="success" icon="pi pi-check" label="Создать"></Button>
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
      availableTags: ["Docker", "Ansible", "IT"],
    }
  },
  mounted() {
    // this.getNote()
    // api_request.get("/api/notes/tags")
    //     .then(
    //         resp => this.tags = resp.data
    //     )
    //     .catch(reason => console.log(reason))
    this.setCkeditorHeight()
    // document.addEventListener("resize", () => {
    //   this.windowHeight = window.innerHeight
    //   this.setCkeditorHeight();
    // })
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
    updateFiles(files){
      this.files = files
    },
    submit() {
      if (this.noteData.title.length === 0) this.errors.title = true;
      if (this.noteData.tags.length === 0) this.errors.tags = true;
      if (this.noteData.content.length === 0) this.errors.content = true;
      if (this.errors.hasErrors()) return
      let form = new FormData()
      for (const file of this.files) {
        form.append("files", file)
      }
      api_request.post("/api/notes/", this.noteData)
          .then(
            resp => {
              api_request.post("/api/notes/files/" + resp.data.id, form)
            }
          )

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