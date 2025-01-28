<template>
  <Header section-name="База знаний" :show-create-button="userPermissions.hasPermissionToCreateNote"/>

  <div class="px-2 py-3">

    <div class="flex-column p-fluid md:px-6 lg:px-8">

      <div class="flex flex-wrap justify-content-end">
        <div class="flex">
          <div v-show="filter.use_vectorizer" >
            <label for="filter.vectorizer_only" class="flex align-items-center p-2 cursor-pointer"
              v-tooltip.top="{
                      value: 'Если включено, то будет использовать только векторный поиск текста',
                      pt: {
                          text: 'w-12rem text-sm'
                      },
                  }">
              <span class="px-2">Только вектор</span>
              <InputSwitch v-model="filter.vectorizer_only" @change="performNewSearch"
                           input-id="filter.vectorizer_only" input-class="text-purple-500" />
            </label>
          </div>

          <Button label="Векторный поиск" icon="pi pi-sparkles" severity="help" size="small"
                  v-tooltip.top="{
                      value: 'Векторный поиск — это метод, который использует технологии машинного обучения для поиска и извлечения информации, наиболее похожей или релевантной данному запросу.',
                      pt: {
                          text: 'w-14rem text-sm'
                      },
                  }"
                  :outlined="!filter.use_vectorizer"
                  @click="() => {filter.toggleVectorSearch(); performNewSearch()}"/>
        </div>
      </div>
      <div class="py-2">
        <AutoComplete class="h-4rem text-900" v-model="filter.search"
                      :input-class="filter.use_vectorizer ? 'border-purple-500 text-purple-500': ''"
                      :input-style="{'text-align': 'center', 'font-size': '1.5rem'}"
                      @keydown.enter="performNewSearch"
                      :suggestions="titles"
                      @complete="autocomplete"
                      @itemSelect="performNewSearch"
                      :input-props="{autofocus: true}"
                      placeholder="Поиск информации">
          <template #empty>
            Заголовок с таким названием не найден
          </template>
        </AutoComplete>
      </div>

      <MultiSelect v-model="filter.tags" :options="tags" filter placeholder="Выберите теги" @change="performNewSearch"
                   scroll-height="320px" :maxSelectedLabels="3" class="w-full md:w-20rem text-sm"/>

      <div class="flex flex-wrap justify-content-center gap-2 py-2">
        <Badge v-for="t in filter.tags">
          <template #default>
            <div class="flex align-items-center gap-2 select-none">
              <span>{{t}}</span>
              <i class="pi pi-times text-sm cursor-pointer" @click="() => deleteTag(t)"/>
            </div>
          </template>
        </Badge>
      </div>

      <div v-if="showTotalCount" class="flex justify-content-center">
        <div class=" border-round-3xl flex justify-content-around p-2 " style="width: 150px;">
          Найдено: {{ totalRecords }}
        </div>
      </div>

    </div>

    <OverlayPanel ref="showFiles">
      <div style="max-height: 300px;" class="files-scrollbar block">
        <div v-if="noteFilesShow" class="flex flex-column">
          <p v-for="file in noteFilesShow.files" class="mr-3 m-2 flex align-items-center">
            <MediaPreview :file="file" :is-file-object="false" :fileNoteID="noteFilesShow.id" :nggroup="'note-attached-images-'+noteFilesShow.id"/>
          </p>
        </div>
      </div>
    </OverlayPanel>


    <div id="notesContainer" class="flex flex-wrap justify-content-center gap-3 pt-3">

      <NoteElement v-for="note in notes" :key="note.id" :note="note" @select:tag="selectTag" @show:preview="showNote" />

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

</template>

<script lang="ts">
import {mapState} from "vuex";

import MediaPreview from "@/components/MediaPreview.vue";
import NoteElement from "@/components/NoteElement.vue";
import ViewNote from "@/components/ViewNote.vue";
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";

import {DetailNote} from "@/note";
import {Paginator} from "@/paginator";
import notesService from "@/services/notes";
import {UserPermissions} from "@/permissions";
import {createNoteFilter, NoteSearchFilter} from "@/filters";

enum FindNotesMode {
  rebase = "rebase",
  append = "append"
}

export default {
  name: "Notes",
  components: {NoteElement, MediaPreview, Footer, ViewNote, Header},
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
  async mounted() {
    this.initPageTitle()
    if (!this.loggedIn) this.$router.push("/login");

    this.userPermissions = new UserPermissions(await notesService.getPermissions());

    this.filter = createNoteFilter(this.$route.query)

    this.findNotes(FindNotesMode.rebase)

    this.tags = await notesService.getAvailableTags();
  },

  computed: {
    ...mapState({loggedIn: (state: any) => state.auth.status.loggedIn}),
  },
  methods: {
    initPageTitle() {
      document.title = 'База Знаний'
    },

    autocomplete(event: any) {
      notesService.autocomplete(event.query).then(titles => this.titles = titles)
    },

    deleteTag(tagName: string): void {
      const tagID = this.filter.tags.indexOf(tagName)
      if (tagID >= 0) {
        this.filter.tags.splice(tagID, 1);
        this.performNewSearch();
      }
    },

    selectTag(tagName: string): void {
      const tagID = this.filter.tags.indexOf(tagName);
      if (tagID >= 0) return;
      this.filter.tags.push(tagName)
      this.showNoteModal = false
      this.performNewSearch()
    },

    // Получение записей на первой странице
    performNewSearch(): void {
      this.paginator.currentPage = 1
      this.findNotes(FindNotesMode.rebase)
    },

    /**
     * Ищет новые записи и согласно указанному типу сохранения `append`, `rebase`
     * добавляет к уже имеющимся записям новые, либо переопределяет их
     * @param {String} save_mode
     */
    findNotes(save_mode: FindNotesMode): void {

      if (save_mode === FindNotesMode.rebase) {
        this.notes = []
        this.paginator = new Paginator()
      }
      this.searchingNotes = true;

      notesService.findNotes(this.filter, this.paginator.currentPage).then(
          resp => {
            if (save_mode === FindNotesMode.append) {
              this.notes.push(...resp.notes)
            } else {
              this.notes = resp.notes
            }
            this.searchingNotes = false;
            this.totalRecords = Number(resp.totalRecords)

            // Показываем кол-во найденых заметок, только если это был поиск по фильтру.
            this.showTotalCount = this.filter.getParamsString().length > 0;

            this.paginator = resp.paginator
          }
      )
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