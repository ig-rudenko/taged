<script lang="ts" setup>

import {PropType, ref} from "vue";
import {NoteDraft} from "@/note.ts";

const props = defineProps({
  note: {
    required: true,
    type: Object as PropType<NoteDraft>
  }
})

const emits = defineEmits(["delete:draft"])

const visibleDeleteModal = ref(false);

function deleteDraft() {
  emits('delete:draft', props.note.id);
  visibleDeleteModal.value = false;
}

</script>

<template>

  <div class="w-22rem">
    <div class="border-round-2xl h-full shadow-3 relative">
      <Button @click="visibleDeleteModal=!visibleDeleteModal" class="absolute top-0 right-0" severity="danger"
              size="small" icon="pi pi-trash"/>

      <router-link :to="'/notes/create?draft=' + note.id" class="h-14rem">
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
              <Tag v-for="tag in note.tags" :value="tag"
                   class="bg-orange-light hover:bg-indigo-500 hover:shadow-4 font-normal cursor-pointer select-none"/>
            </div>
          </div>
          <h2>{{ note.title || "черновик" }}</h2>
        </div>

      </div>
    </div>
  </div>

  <Dialog v-model:visible="visibleDeleteModal" header="Удалить черновик?" :closable="false">
    <div class="flex gap-2 justify-content-center">
      <Button icon="pi pi-times" label="Нет" @click="visibleDeleteModal=false"/>
      <Button icon="pi pi-check" severity="danger" label="Да " @click="deleteDraft"/>
    </div>
  </Dialog>

</template>

<style scoped>

</style>