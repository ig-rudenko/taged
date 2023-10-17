<template>
  <Header section-name="База знаний" section-description="Здесь вы можете найти необходимую для вас информацию"
          :show-create-button="true"/>

  <div class="px-4 md:px-6 lg:px-8">

    <div class="py-8 flex-column p-fluid">
      <AutoComplete class="h-4rem text-900" v-model.trim="search"
                    :input-style="{'text-align': 'center', 'font-size': '1.5rem'}"
                    @keydown.enter="getNotes"
                    :suggestions="titles"
                    @complete="autocomplete"
                    @itemSelect="getNotes"
                    placeholder="Поиск информации">
        <template #empty>
          Заголовок с таким названием не найден
        </template>
      </AutoComplete>
      <MultiSelect v-model="tagsSelected" :options="tags" filter placeholder="Выберите теги"
                   @change="getNotes" scroll-height="400px"
                   :maxSelectedLabels="3" class="w-full md:w-20rem" />
    </div>

    <Dialog style="max-height: 100%" v-model:visible="showNoteModal" modal :show-header="true" :style="{ width: '100vw', height: '100%' }">
      <ViewNote @selected-tag="selectTag" :note-id="showNoteID"/>
    </Dialog>

    <div class="flex flex-wrap justify-content-center">

        <div class="w-30rem p-3" v-for="note in notes">

          <Badge v-if="note.score>0.05" :class="badgeClasses(note)" :value="'match: '+Math.round(note.score * 100)+'%'" />

          <div :class="noteClasses(note)" style="height: 100%">
            <div class="flex justify-content-center cursor-pointer">
              <img v-if="note.previewImage" :src="note.previewImage" class="border-round-2xl p-2 border-round-2xl" style="max-height: 230px; width: 100%">
              <svg v-else class="border-round-top-2xl cursor-pointer" width="100%" height="225" xmlns="http://www.w3.org/2000/svg"
                   role="img" aria-label="Placeholder: Thumbnail" preserveAspectRatio="xMidYMid slice" focusable="false">
                <title>Placeholder</title>
                <rect width="100%" height="100%" fill="#aaaaaa"></rect>
                <text x="38%" y="50%" fill="#eceeef" dy=".3em">Нет изображения</text>
              </svg>
            </div>

            <div class="p-3">
              <div class="flex flex-wrap justify-content-between align-items-center">
                <div>
                  <Tag class="bg-orange-light hover:bg-indigo-500 hover:shadow-4 mr-2 font-normal cursor-pointer" @click="selectTag(tag)" v-for="tag in note.tags" :value="tag"/>
                </div>
                <i v-if="note.filesCount>0" v-badge="note.filesCount" class="pi pi-file p-overlay-badge" style="font-size: 2rem" />
              </div>

              <p>{{ note.title }}</p>
              <div class="flex justify-content-end">
                <Button size="small" rounded class="bg-orange-light border-0" icon="pi pi-eye" @click="showNote(note.id)"></Button>
              </div>
              <div>
                <small class="text-black-alpha-60"><i class="pi pi-calendar"/> {{ note.published_at }}</small>
              </div>
            </div>
          </div>
        </div>

      </div>

  </div>

  <Footer/>

  <ScrollTop />

</template>

<script>
import Badge from "primevue/badge/Badge.vue";
import Dialog from "primevue/dialog/Dialog.vue";
import MultiSelect from "primevue/multiselect/MultiSelect.vue";
import AutoComplete  from "primevue/autocomplete/AutoComplete.vue";
import Button from "primevue/button/Button.vue"
import Header from "./components/Header.vue";
import ViewNote from "./components/ViewNote.vue";
import Tag from "primevue/tag/Tag.vue";
import ScrollTop from 'primevue/scrolltop';
import Footer from "./components/Footer.vue";
import api_request from "./api_request.js";

export default {
  name: "Notes",
  components: {
    AutoComplete,
    Badge,
    Footer,
    Dialog,
    MultiSelect,
    ViewNote,
    Header,
    Button,
    Tag,
    ScrollTop,
  },
  data() {
    return {
      showNoteID: null,
      showNoteModal: false,
      search: "",
      tagsSelected: [],
      titles: [],
      notes: [],
      tags: [],
      totalRecords: 0,
      paginator: {
        currentPage: 1,
        maxPages: 1,
        perPage: 24,
      }
    }
  },
  mounted() {
    this.getNotes()
    api_request.get("/api/notes/tags")
        .then(
            resp => this.tags = resp.data
        )
        .catch(reason => console.log(reason))
  },
  methods: {
    autocomplete(event) {
      api_request.get("/api/notes/autocomplete?term=" + event.query)
          .then(
            resp => this.titles = resp.data
          )
          .catch(
              reason => console.log(reason)
          )
    },
    noteClasses(note) {
      let classes = ["border-round-2xl"]
      if (note.score > 0.9) {
        classes.push("total-match")
      } else {
        classes.push("shadow-2")
      }
      return classes
    },
    badgeClasses(note) {
      let classes = ["absolute", "m-2"]
      if (note.score > 0.9) {
        classes.push("bg-purple-light")
      } else if (note.score < 0.2) {
        classes.push("shadow-2")
      }
      return classes
    },
    selectTag(tagName) {
      this.tagsSelected = [tagName]
      this.showNoteModal = false
      this.getNotes()
    },
    getNotes() {
      let url = "/api/notes/?"
      url += "page=" + this.paginator.currentPage
      url += "&search=" + this.search
      for (const tag of this.tagsSelected) {
        url += "&tags-in=" + tag
      }
      api_request.get(url)
          .then(
              resp => {
                this.notes = resp.data.records
                this.totalRecords = resp.data.totalRecords
                this.paginator = resp.data.paginator
              }
          )
          .catch(
              reason => console.log(reason)
          )
    },
    showNote(note_id) {
      this.showNoteID = note_id;
      this.showNoteModal = true
    }
  }
}
</script>

<style scoped>
html, body {
  margin: 0!important;
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