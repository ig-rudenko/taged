<template>

  <Header :section-name="editNoteID?'Редактирование записи':'Создание новой записи'" :show-count="false"/>

  <NoteForm @submit:form="submit" :note="note" :noteID="editNoteID" :submit-in-process="submitInProcess"/>
  <Footer/>

</template>

<script lang="ts">
import {mapState} from "vuex";

import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import {Note, NoteDraft} from "@/note";
import notesService from "@/services/notes";
import NoteForm from "@/components/NoteForm.vue";

export default {
  name: "Notes",
  components: {NoteForm, Header, Footer},
  data() {
    return {
      note: new Note() as Note,
      editNoteID: null as string|null,
      draftID: null as string|null,
      lastDraft: undefined as NoteDraft|undefined,
      submitInProcess: false,
    }
  },

  async mounted() {
    if (!this.user) await this.$router.push("/login");

    // Проверяем, не является ли данная ссылка редактированием существующей записи
    this.editNoteID = this.$route.params.id?.toString() || null
    if (this.editNoteID) {
      // В таком случае получаем её данные
      await this.getNote()
      document.title = "Редактирование: " + this.note.title;
    } else {
      document.title = "Создание записи";
      this.draftID = this.$route.query.draft?.toString() || null;
      await this.getNoteFromDraft();
      setTimeout(this.autoSaveDraft);
    }
  },

  computed: {
    ...mapState({user: (state: any) => state.auth.user}),
  },

  methods: {
    async getNoteFromDraft() {
      if (!this.draftID) return;

      this.lastDraft = await notesService.getDraft(this.draftID);
      if (!this.lastDraft) return;
      this.note.title = this.lastDraft.title;
      this.note.content = this.lastDraft.content;
      this.note.tags = this.lastDraft.tags;
    },

    async autoSaveDraft() {
      setTimeout(this.autoSaveDraft, 4000)

      // Если нет данных, то пропускаем проверку черновика
      if (!this.note.title && !this.note.content && !this.note.tags.length) return;

      // Если идет процесс создания записи, то не проверяем черновик.
      if (this.submitInProcess) return;

      // Если нет изменений, то не обновляем черновик.
      if (this.lastDraft &&
          this.lastDraft.title == this.note.title &&
          this.lastDraft.content == this.note.content &&
          this.lastDraft.tags == this.note.tags) return;

      // Если нет черновика, то создаем
      if (!this.draftID || !this.lastDraft) {
        this.lastDraft = await notesService.createDraft(this.note);
        this.draftID = this.lastDraft.id;
        return;
      }

      // Обновляем черновик.
      this.lastDraft = await notesService.saveDraft(this.draftID, this.note);
    },

    async getNote() {
      if (!this.editNoteID) return;
      this.note = await notesService.getNote(this.editNoteID);
    },

    /** Подтверждаем данные заметки */
    async submit(note: Note, files: File[]) {
      if (!note.isValid() || this.submitInProcess) return;

      this.submitInProcess = true

      let filesForm = new FormData()
      for (const file of files) {
        filesForm.append("files", file)
      }

      let pushTo: string;
      if (this.editNoteID) {
        await notesService.updateNote(note, filesForm);
        pushTo = "/notes/" + this.editNoteID;
      } else {
        await notesService.createNote(note, filesForm);
        pushTo = "/notes/";
      }

      // Удаляем черновик
      if (this.draftID) await notesService.deleteDraft(this.draftID);

      // Перенаправляем
      await this.$router.push(pushTo);
      this.submitInProcess = false;
    },

  }
}
</script>

<style scoped>
html, body {
  margin: 0 !important;
}
</style>