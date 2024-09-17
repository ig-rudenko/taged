<template>
  <Header section-name="База знаний" section-description="Здесь вы можете найти необходимую для вас информацию"
          :show-create-button="userPermissions.hasPermissionToCreateNote"/>
  <div class="px-2">

    <div class="flex-column p-fluid md:px-6 lg:px-8">
      <div class="p-inputgroup flex-1">
        <AutoComplete class="h-4rem text-900" v-model="filter.search"
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
      <MultiSelect v-model="filter.tags" :options="tags" filter placeholder="Выберите теги" @change="performNewSearch"
                   scroll-height="400px" :maxSelectedLabels="3" class="w-full md:w-20rem"
                   :class="filter.tags.length?'border-primary-500':''"/>

      <div v-if="showTotalCount" class="flex justify-content-center">
        <div class="bg-indigo-500 border-round-3xl flex justify-content-around p-2 text-white" style="width: 150px;">
          Найдено: {{ totalRecords }}
        </div>
      </div>

    </div>

    <OverlayPanel ref="showFiles">
      <div style="max-height: 300px;" class="files-scrollbar block">
        <div v-if="noteFilesShow" class="flex flex-column">
          <p v-for="file in noteFilesShow.files" class="mr-3 m-2 flex align-items-center">
            <MediaPreview :file="file" :is-file-object="false" :fileNoteID="noteFilesShow.id"/>
          </p>
        </div>
      </div>
    </OverlayPanel>


    <div id="notesContainer" class="flex flex-wrap justify-content-center">
      <div class="w-30rem p-2 m-1" v-for="note in notes">

        <Badge v-if="note.score>0.05" :class="badgeClasses((<DetailNote>note))"
               :value="'match: '+note.scorePercents+'%'"/>

        <div :class="noteClasses((<DetailNote>note))" style="height: 100%">
          <a :href="'/notes/' + note.id"
             class=" flex justify-content-center align-content-center align-items-center cursor-pointer"
             style="min-height: 230px;">
            <img v-if="note.previewImage?.length" :src="note.previewImage"
                 class="border-round-2xl p-2 border-round-2xl" style="max-height: 230px; max-width: 100%;"
                 alt="preview">
            <svg v-else class="border-round-top-2xl cursor-pointer" width="100%" height="225"
                 xmlns="http://www.w3.org/2000/svg"
                 role="img" aria-label="Placeholder: Thumbnail" preserveAspectRatio="xMidYMid slice" focusable="false">
              <rect width="100%" height="100%" fill="#aaaaaa"></rect>
              <text x="38%" y="50%" fill="#eceeef" dy=".3em">Нет изображения</text>
            </svg>
          </a>

          <div class="p-3">
            <div class="flex flex-wrap justify-content-between align-items-center gap-3">
              <div class="flex flex-wrap gap-1">
                <Tag @click="selectTag(tag)" v-for="tag in note.tags" :value="tag"
                     class="bg-orange-light hover:bg-indigo-500 hover:shadow-4 font-normal cursor-pointer"/>
              </div>
              <i v-if="note.filesCount>0" @click="e => showNoteFiles((<DetailNote>note), e)"
                 v-badge="note.filesCount" class="pi pi-file p-overlay-badge cursor-pointer" style="font-size: 2rem"/>
            </div>

            <h2>{{ note.title }}</h2>
            <div class="flex justify-content-end">
              <Button size="small" rounded class="bg-orange-light border-0" icon="pi pi-eye"
                      @click="showNote(note.id)"></Button>
            </div>
            <div>
              <small class="text-black-alpha-60"><i class="pi pi-calendar"/> {{ note.published_at }}</small>
            </div>
          </div>
        </div>
      </div>

    </div>

    <div v-if="searchingNotes" class="text-center p-3">
      <i class="pi pi-spinner pi-spin text-6xl"/>
    </div>

    <div v-if="paginator.currentPage < paginator.maxPages" @click="addNextPage"
         class="pt-4 align-items-center cursor-pointer flex flex-column" style="font-size: 1.2rem;">
      <div>Больше</div>
      <i class="p-button-icon pi pi-angle-double-down" data-pc-section="icon" style="font-size: 1.5rem;"/>
    </div>

  </div>


  <Dialog id="notePreviewDialog" v-if="showNoteID" style="max-height: 100%;" v-model:visible="showNoteModal" modal
          :show-header="true" @afterHide="initPageTitle" :style="{ width: '100vw', height: '100%' }">
    <ViewNote @selected-tag="selectTag" :note-id="showNoteID" :remove-padding="true"/>
  </Dialog>


  <Footer/>

  <ScrollTop/>

</template>

<script lang="ts">
import Badge from "primevue/badge/Badge.vue";
import Dialog from "primevue/dialog/Dialog.vue";
import MultiSelect from "primevue/multiselect/MultiSelect.vue";
import AutoComplete from "primevue/autocomplete/AutoComplete.vue";
import Button from "primevue/button/Button.vue"
import OverlayPanel from "primevue/overlaypanel";
import Tag from "primevue/tag/Tag.vue";
import ScrollPanel from "primevue/scrollpanel";
import ScrollTop from 'primevue/scrolltop';

import MediaPreview from "@/components/MediaPreview.vue";
import ViewNote from "@/components/ViewNote.vue";
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import api from "@/services/api";
import {Paginator} from "@/paginator";
import {UserPermissions} from "@/permissions";
import {DetailNote, getFiles, newDetailNote} from "@/note";
import {createNoteFilter, NoteSearchFilter} from "@/filters.ts";
import {mapState} from "vuex";

enum FindNotesMode {
  rebase = "rebase",
  append = "append"
}

export default {
  name: "Notes",
  components: {
    MediaPreview,
    AutoComplete,
    Badge,
    Footer,
    Dialog,
    MultiSelect,
    ViewNote,
    OverlayPanel,
    Header,
    Button,
    Tag,
    ScrollTop,
    ScrollPanel,
  },
  data() {
    return {
      searchingNotes: false,

      showNoteID: null as string | null,
      showNoteModal: false,
      titles: [] as string[],
      notes: [] as DetailNote[],
      tags: [] as string[],
      totalRecords: 0,
      paginator: new Paginator(),
      userPermissions: new UserPermissions([]),
      showTotalCount: false,
      noteFilesShow: null as DetailNote | null,

      filter: new NoteSearchFilter()
    }
  },
  mounted() {
    this.initPageTitle()
    if (!this.loggedIn) this.$router.push("/login");

    api.get("/notes/permissions").then(resp => {
      this.userPermissions = new UserPermissions(resp.data)
    })

    this.filter = createNoteFilter(this.$route.query)

    this.findNotes(FindNotesMode.rebase)

    api.get("/notes/tags").then(resp => this.tags = resp.data).catch(reason => console.log(reason))
  },

  computed: {
    ...mapState({loggedIn: (state: any) => state.auth.status.loggedIn}),
    DetailNote() {
      return DetailNote
    }
  },
  methods: {
    initPageTitle() {
      document.title = 'База Знаний'
    },

    autocomplete(event: any) {
      api.get("/notes/autocomplete?term=" + event.query).then(resp => this.titles = Array.from(resp.data))
          .catch(reason => console.log(reason))
    },

    noteClasses(note: DetailNote): string[] {
      let classes = ["border-round-2xl"]
      if (note.score > 0.9) {
        classes.push("total-match")
      } else {
        classes.push("shadow-4")
      }
      return classes
    },

    badgeClasses(note: DetailNote): string[] {
      let classes = ["absolute", "m-2"]
      if (note.score > 0.9) {
        classes.push("bg-purple-light")
      } else if (note.score < 0.2) {
        classes.push("shadow-2")
      }
      return classes
    },

    showNoteFiles(note: DetailNote, event: Event) {
      if (note.files.length > 0) {
        this.noteFilesShow = note;
        (<OverlayPanel>this.$refs.showFiles).toggle(event, event.target)
        return
      }

      api.get("/notes/" + note.id + "/files").then(
          resp => {
            note.files = getFiles(resp.data);
            this.noteFilesShow = note;
            (<OverlayPanel>this.$refs.showFiles).toggle(event, event.target)
          }
      )
    },

    selectTag(tagName: string): void {
      this.filter.tags = [tagName]
      this.showNoteModal = false
      this.performNewSearch()
    },

    // Получение записей на первой странице
    performNewSearch(): void {
      this.paginator.currentPage = 1
      this.findNotes(FindNotesMode.rebase)
      this.showTotalCount = true
    },

    /**
     * Ищет новые записи и согласно указанному типу сохранения `append`, `rebase`
     * добавляет к уже имеющимся записям новые, либо переопределяет их
     * @param {String} save_mode
     */
    findNotes(save_mode: FindNotesMode): void {
      const params = this.filter.getParams()
      const filterParamsString = this.filter.getParamsString()

      params.append("page", String(this.paginator.currentPage))

      history.pushState({path: "/" + filterParamsString}, '', "/" + filterParamsString);

      let apiURL = "/notes/?" + params.toString()

      if (save_mode === FindNotesMode.rebase) {
        this.notes = []
        this.paginator = new Paginator()
      }
      this.searchingNotes = true;

      api.get(apiURL).then(
          resp => {
            if (save_mode === FindNotesMode.append) {
              this.notes.push(...this.getDetailNotes(resp.data.records))
            } else {
              this.notes = this.getDetailNotes(resp.data.records)
            }
            this.searchingNotes = false;
            this.totalRecords = Number(resp.data.totalRecords)
            this.paginator = new Paginator(
                resp.data.paginator.currentPage,
                resp.data.paginator.maxPages,
                resp.data.paginator.perPage
            )
          }
      ).catch(reason => console.log(reason))
    },

    getDetailNotes(data: any[]): Array<DetailNote> {
      let res: Array<DetailNote> = []
      for (const note of data) {
        res.push(newDetailNote(note))
      }
      return res
    },

    addNextPage(): void {
      this.paginator.currentPage++
      if (this.paginator.currentPage <= this.paginator.maxPages) {
        this.findNotes(FindNotesMode.append)
      }
    },

    showNote(note_id: string): void {
      this.showNoteID = note_id;
      this.showNoteModal = true
    },
  }
}
</script>

<style scoped>
html, body {
  margin: 0 !important;
}

.files-scrollbar {
  overflow: auto;
}

.files-scrollbar::-webkit-scrollbar {
  display: inline !important;
  width: 7px !important;
  height: 5px !important;
}

.files-scrollbar::-webkit-scrollbar-track-piece {
  background-color: var(--primary-100) !important;
  border-radius: 20px !important;
  opacity: 0.3 !important;
}

.files-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--primary-300) !important;
  border-radius: 20px !important;
  height: 4px !important;
}

.files-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: var(--primary-500) !important;
}

@media (max-width: 600px) {
  #notesContainer > div {
    margin: 0!important;
    padding: 0.7rem 0!important;
  }
}

</style>