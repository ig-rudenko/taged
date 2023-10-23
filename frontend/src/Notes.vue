<template>
  <Header section-name="База знаний" section-description="Здесь вы можете найти необходимую для вас информацию"
          :show-create-button="showCreateButton"/>

  <div class="md:px-6 lg:px-8">

    <div class="flex-column p-fluid">
      <div class="p-inputgroup flex-1">
        <AutoComplete class="h-4rem text-900" v-model="search"
                      :input-style="{'text-align': 'center', 'font-size': '1.5rem'}"
                      @keydown.enter="performNewSearch"
                      :suggestions="titles"
                      @complete="autocomplete"
                      @itemSelect="performNewSearch"
                      :auto-option-focus="false"
                      placeholder="Поиск информации">
          <template #empty>
            Заголовок с таким названием не найден
          </template>
        </AutoComplete>
      </div>
      <MultiSelect v-model="tagsSelected" :options="tags" filter placeholder="Выберите теги"
                   @change="performNewSearch" scroll-height="400px"
                   :maxSelectedLabels="3" class="w-full md:w-20rem" />

      <div v-if="showTotalCount" class="flex justify-content-center">
        <div class="bg-indigo-500 border-round-3xl flex justify-content-around p-2 text-white" style="width: 150px;">
          Найдено: {{ totalRecords }}
        </div>
      </div>

    </div>



    <Dialog style="max-height: 100%" v-model:visible="showNoteModal" modal :show-header="true" :style="{ width: '100vw', height: '100%' }">
      <ViewNote @selected-tag="selectTag" :note-id="showNoteID"/>
    </Dialog>



    <div class="flex flex-wrap justify-content-center">

        <div class="w-30rem p-3" v-for="note in notes">

          <Badge v-if="note.score>0.05" :class="badgeClasses(note)" :value="'match: '+Math.round(note.score * 100)+'%'" />

          <div :class="noteClasses(note)" style="height: 100%">
            <a :href="'/notes/' + note.id" class=" flex justify-content-center align-content-center align-items-center cursor-pointer" style="min-height: 230px;">
              <img v-if="note.previewImage" :src="note.previewImage"
                   class="border-round-2xl p-2 border-round-2xl" style="max-height: 230px; max-width: 100%;">
              <svg v-else class="border-round-top-2xl cursor-pointer" width="100%" height="225" xmlns="http://www.w3.org/2000/svg"
                   role="img" aria-label="Placeholder: Thumbnail" preserveAspectRatio="xMidYMid slice" focusable="false">
                <title>Placeholder</title>
                <rect width="100%" height="100%" fill="#aaaaaa"></rect>
                <text x="38%" y="50%" fill="#eceeef" dy=".3em">Нет изображения</text>
              </svg>
            </a>

            <div class="p-3">
              <div class="flex flex-wrap justify-content-between align-items-center">
                <div>
                  <Tag class="bg-orange-light hover:bg-indigo-500 hover:shadow-4 mr-2 font-normal cursor-pointer" @click="selectTag(tag)" v-for="tag in note.tags" :value="tag"/>
                </div>
                <i v-if="note.filesCount>0" v-badge="note.filesCount" class="pi pi-file p-overlay-badge" style="font-size: 2rem" />
              </div>

              <h2>{{ note.title }}</h2>
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


    <div @click="addNextPage" class="pt-4 align-items-center cursor-pointer flex flex-column" style="font-size: 1.2rem;">
        <div>Больше</div>
        <i class="p-button-icon pi pi-angle-double-down" data-pc-section="icon" style="font-size: 1.5rem;" />
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
      },
      userPermissions: [],
      showTotalCount: false,
    }
  },
  mounted() {
    api_request.get("/api/notes/permissions").then(resp => {this.userPermissions = resp.data})

    this.findNotes('rebase')

    api_request.get("/api/notes/tags")
        .then(
            resp => this.tags = resp.data
        )
        .catch(reason => console.log(reason))
  },

  computed: {
    showCreateButton() {
      return this.userPermissions.includes("create_notes")
    }
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
        classes.push("shadow-4")
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
      this.performNewSearch()
    },

    // Получение записей на первой странице
    performNewSearch() {
      this.paginator.currentPage = 1
      this.findNotes('rebase')
      this.showTotalCount = true
    },

    /**
     * Ищет новые записи и согласно указанному типу сохранения `append`, `rebase`
     * добавляет к уже имеющимся записям новые, либо переопределяет их
     * @param {String} save_mode
     */
    findNotes(save_mode) {
      let url = "/api/notes/?"
      url += "page=" + this.paginator.currentPage
      url += "&search=" + this.search
      for (const tag of this.tagsSelected) {
        url += "&tags-in=" + tag
      }
      api_request.get(url)
          .then(
              resp => {
                if (save_mode === 'append') {
                  this.notes.push(...resp.data.records)
                } else {
                  this.notes = resp.data.records
                }
                this.totalRecords = resp.data.totalRecords
                this.paginator = resp.data.paginator
              }
          )
          .catch(reason => console.log(reason))
    },

    addNextPage() {
      this.paginator.currentPage++
      if (this.paginator.currentPage <= this.paginator.maxPages) {
        this.findNotes('append')
      }
    },

    showNote(note_id) {
      this.showNoteID = note_id;
      this.showNoteModal = true
    },
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