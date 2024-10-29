<script lang="ts">
import {defineComponent, PropType} from 'vue';

import LoadMedia from "@/components/LoadMedia.vue";
import MediaPreview from "@/components/MediaPreview.vue";
import notesService from "@/services/notes";
import {Note, NoteFile} from "@/note";
import CKEditorForm from "@/components/CKEditorForm.vue";

export default defineComponent({
  name: "NoteForm",
  components: {CKEditorForm, MediaPreview, LoadMedia},
  props: {
    noteID: {required: false, type: String as PropType<string|null>, default: null},
    note: {required: false, type: Object as PropType<Note>, default: new Note()},
    submitInProcess: {required: false, type: Boolean, default: false},
  },

  emits: ["submit:form"],

  data() {
    return {
      userPermissions: [] as string[],
      availableTags: [] as string[],
      files: [] as File[],
      showAddTagInput: false,
      newTag: "",
    }
  },

  async mounted() {
    notesService.getPermissions().then(data => this.userPermissions = data);
    notesService.getAvailableTags().then(data => this.availableTags = data);
  },

  computed: {
    hasPermissionToCreateTag() {
      return this.userPermissions.includes("add_tags")
    },
  },
  methods: {
    submit(){
      this.$emit('submit:form', this.note, this.files);
    },

    updateFiles(files: File[]) {
      this.files = files
    },

    toggleFile(file: NoteFile) {
      file.disable = !file.disable
    },

    addNewTag() {
      if (!this.newTag.length) return;
      this.availableTags.push(this.newTag)
      this.note?.tags.push(this.newTag)
      this.newTag = ""
    },
  }
})
</script>

<template>

  <div class="lg:px-8">

    <div class="px-3">
      <Button v-if="submitInProcess" severity="success" icon="pi pi-spin pi-spinner"
              :label="noteID?'Обновляется':'Создается'"/>
      <Button v-else @click="submit" severity="success" icon="pi pi-check" :label="noteID?'Обновить':'Создать'"/>
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

        <div v-if="noteID && note.files.length" class="align-items-end flex flex-column">
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
                                :max-file-name-length="20" :fileNoteID="noteID"/>
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
      <CKEditorForm :skipInitialImages="noteID != null" :text="note.content" @update:text="(v: string) => note.content = v" />
    </div>

  </div>
</template>

<style scoped>
@media (width < 786px) {
  #select-tags {
    width: 100% !important;
  }
}
</style>