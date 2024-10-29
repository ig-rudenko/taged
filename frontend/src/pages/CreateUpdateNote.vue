<template>

  <Header :section-name="editNoteID?'Редактирование записи':'Создание новой записи'" :show-count="false"/>

  <NoteForm @submit:form="submit" :note="note" :noteID="editNoteID" :submit-in-process="submitInProcess"/>
  <Footer/>

</template>

<script lang="ts">
import {mapState} from "vuex";

import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import {Note} from "@/note";
import notesService from "@/services/notes";
import NoteForm from "@/components/NoteForm.vue";

export default {
  name: "Notes",
  components: {NoteForm, Header, Footer},
  data() {
    return {
      note: new Note() as Note,
      editNoteID: null as string|null,
      submitInProcess: false,
    }
  },

  async mounted() {
    if (!this.user) await this.$router.push("/login");

    // Проверяем, не является ли данная ссылка редактированием существующей записи
    this.editNoteID = this.$route.params.id.toString()
    if (this.editNoteID) {
      // В таком случае получаем её данные
      await this.getNote()
      document.title = "Редактирование: " + this.note.title;
    } else {
      document.title = "Создание записи";
    }
  },

  computed: {
    ...mapState({user: (state: any) => state.auth.user}),
  },

  methods: {
    async getNote() {
      if (this.editNoteID) {
        const note = await notesService.getNote(this.editNoteID);
        this.note.title = note.title
        this.note.content = note.content
        this.note.tags = note.tags
        this.note.files = note.files
        this.note.id = note.id
      }
    },

    /** Подтверждаем данные заметки */
    async submit(note: Note, files: File[]) {
      if (!note.isValid() || this.submitInProcess) return;

      this.submitInProcess = true

      let filesForm = new FormData()
      for (const file of files) {
        filesForm.append("files", file)
      }

      if (this.editNoteID) {
        await notesService.updateNote(note, filesForm);
        await this.$router.push("/notes/" + this.editNoteID);
      } else {
        await notesService.createNote(note, filesForm);
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
</style>