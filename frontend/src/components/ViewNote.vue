<template>
  <div v-if="noteData" class="surface-section px-4 md:px-6 lg:px-8">

    <div class="border-blue-600 font-medium text-2xl p-3 mb-3 text-900" style="border-left: 8px solid;">
      {{ noteData.title }}
    </div>
    <div class="text-600 text-sm mb-3">
      <span class="font-bold"><i class="pi pi-calendar"/> {{ noteData.published_at }}</span>
    </div>


    <!-- TAGS -->
    <div class="mb-5">
      <Tag class="bg-orange-light hover:bg-indigo-500 hover:shadow-4 mr-2 cursor-pointer font-normal" @click="$emit('selected-tag', tag)" v-for="tag in noteData.tags" :value="tag"/>
    </div>

    <div class="mb-5 flex flex-wrap">
      <a v-for="file in noteData.files"
         :href="'/notes/download/'+noteId+'/'+file.name"
         class="mr-3 flex align-items-center no-underline text-900">
        <img class="mr-2" :src="'/static/'+file.icon" height="48" width="48">
        <span class="font-normal">
          {{ file.name }}<br>
          <span class="text-400" style="font-size: 0.8rem">{{ file.size }}</span>
        </span>
      </a>
    </div>

    <hr>

    <!-- CONTENT -->
    <div v-html="noteData.content"></div>

    <ScrollTop />
  </div>


</template>

<script>
import Tag from "primevue/tag/Tag.vue";
import ScrollTop from "primevue/scrolltop/ScrollTop.vue";

import api_request from "../api_request.js";

export default {
  name: "ViewNote",
  components: {
    Tag,
    ScrollTop,
  },
  props: {
    noteId: {required: true, type: String}
  },
  mounted() {
    api_request.get("/api/notes/get/"+this.noteId).then(resp => this.noteData = resp.data)
  },
  data() {
    return {
      noteData: null,
    }
  }
}
</script>

<style scoped>
.bg-orange-light {
  background-color: #FEAA69;
}
</style>