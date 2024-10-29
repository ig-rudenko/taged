<script lang="ts">
import {defineComponent} from 'vue'
import {NoteDraft} from "@/note.ts";
import notesService from "@/services/notes.ts";
import DraftElement from "@/components/DraftElement.vue";

export default defineComponent({
  name: "DraftsList",
  components: {DraftElement},

  data() {
    return {
      showDialog: false,
      drafts: [] as NoteDraft[]
    }
  },

  mounted() {
    this.getDrafts()
  },

  methods: {
    getDrafts() {
      notesService.getDraftsList().then(value => this.drafts = value)
    },

    deleteDraft(id: string): void {
      notesService.deleteDraft(id).then(() => this.getDrafts())
    }
  }

})
</script>

<template>
  <Button @click="showDialog=!showDialog" rounded text icon="pi pi-list" label="Черновики"
          :badge="drafts.length?drafts.length.toString():''" badgeSeverity="danger"/>

  <Dialog v-model:visible="showDialog" modal header="Черновики">
    <div v-if="drafts.length" class="p-2 flex flex-wrap gap-3 justify-content-center">
      <DraftElement v-for="draft in drafts" :key="draft.id" :note="draft" @delete:draft="deleteDraft"/>
    </div>

    <div v-else class="flex justify-content-center w-30rem">
      <h2>У вас нет черновиков</h2>
    </div>

  </Dialog>

</template>

<style scoped>

</style>