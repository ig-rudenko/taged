<script lang="ts" setup>
import {DetailNote} from "@/note";
import OverlayPanel from "primevue/overlaypanel";
import notesService from "@/services/notes.ts";
import MediaPreview from "@/components/MediaPreview.vue";
import {ref} from "vue";

defineProps({
  note: {
    required: true,
    type: DetailNote,
  }
})

const showFiles = ref();

const emits = defineEmits(["select:tag", "show:preview"])

function badgeClasses(note: DetailNote): string[] {
  let classes = ["absolute", "m-2"]
  if (note.score > 0.9) {
    classes.push("bg-purple-light")
  } else if (note.score < 0.2) {
    classes.push("shadow-2")
  }
  return classes
}

function noteClasses(note: DetailNote): string[] {
  let classes = ["border-round-2xl"]
  if (note.score > 0.9) {
    classes.push("total-match")
  } else {
    classes.push("shadow-3")
  }
  return classes
}

function showNoteFiles(note: DetailNote, event: Event) {
  if (note.files.length > 0) {
    showFiles.value.toggle(event, event.target)
    return
  }

  notesService.getNoteFiles(note.id).then(
      files => {
        note.files = files;
        showFiles.value.toggle(event, event.target)
      }
  )
}

</script>

<template>
  <div class="w-22rem">
    <Badge v-if="note.score>0.05" :class="badgeClasses(note)" :value="'match: '+note.scorePercents+'%'"/>

    <div :class="noteClasses(note)" class="h-full">

      <router-link :to="'/notes/' + note.id" class="h-14rem">
        <img v-if="note.previewImage?.length" :src="note.previewImage"
             class="border-round-top-2xl max-h-14rem w-full" style="object-fit: cover" alt="preview">
        <svg v-else class="border-round-top-2xl cursor-pointer h-14rem w-full" width="100%" height="225"
             xmlns="http://www.w3.org/2000/svg"
             role="img" aria-label="Placeholder: Thumbnail" preserveAspectRatio="xMidYMid slice" focusable="false">
          <rect width="100%" height="100%" fill="#aaaaaa"></rect>
          <text x="30%" y="50%" fill="#eceeef" dy=".3em">Нет изображения</text>
        </svg>
      </router-link>

      <div class="p-3 flex flex-column justify-content-between">
        <div>
          <div class="flex flex-wrap justify-content-between align-items-center gap-3">
            <div class="flex flex-wrap gap-1">
              <Tag @click="() => emits('select:tag', tag)" v-for="tag in note.tags" :value="tag"
                   class="bg-orange-light hover:bg-indigo-500 hover:shadow-4 font-normal cursor-pointer select-none"/>
            </div>
            <i v-if="note.filesCount>0" @click="e => showNoteFiles((<DetailNote>note), e)"
               v-badge="note.filesCount" class="pi pi-file p-overlay-badge cursor-pointer" style="font-size: 1.5rem"/>
          </div>
          <h2>{{ note.title }}</h2>
        </div>

        <div class="flex align-items-center justify-content-between ">
          <div><small class="text-black-alpha-60"><i class="pi pi-calendar"/> {{ note.published_at }}</small></div>
          <div class="flex justify-content-end">
            <Button size="small" rounded class="bg-orange-light hover:bg-indigo-500 border-0" icon="pi pi-eye"
                    @click="() => emits('show:preview', note.id)"></Button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <OverlayPanel ref="showFiles">
    <div style="max-height: 300px;" class="files-scrollbar block">
      <div v-if="note" class="flex flex-column">
        <p v-for="file in note.files" class="mr-3 m-2 flex align-items-center">
          <MediaPreview :file="file" :is-file-object="false" :fileNoteID="note.id" :nggroup="'note-attached-images-'+note.id"/>
        </p>
      </div>
    </div>
  </OverlayPanel>

</template>

<style scoped>

</style>