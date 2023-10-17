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
      <Tag v-for="tag in noteData.tags" :value="tag"
           class="bg-orange-light hover:bg-indigo-500 hover:shadow-4 mr-2 cursor-pointer font-normal"
           @click="$emit('selected-tag', tag)"/>
    </div>

    <div class="mb-5 flex flex-wrap">
      <p v-for="file in noteData.files" class="mr-3 flex align-items-center">
        <Image v-if="isImage(file.name)"
               :src="getFileDownloadURL(file.name)" :alt="file.name"
               class="mr-2" :image-style="{'max-height': '64px', 'max-width': '64px'}" preview />

        <!-- Иконка формата файла -->
        <img v-else class="mr-2" :src="'/static/'+file.icon" height="48" width="48" :alt="file.name">

        <a :href="getFileDownloadURL(file.name)" class="font-normal no-underline text-900">
          {{ file.name }}<br>
          <span class="text-400" style="font-size: 0.8rem">{{ formatBytes(file.size) }}</span>
        </a>
      </p>
    </div>

    <hr>

    <!-- CONTENT -->
    <div v-html="noteData.content"></div>

    <ScrollTop />
  </div>


</template>

<script>
import Tag from "primevue/tag/Tag.vue";
import Image from "primevue/image/Image.vue";
import ScrollTop from "primevue/scrolltop/ScrollTop.vue";

import api_request from "../api_request.js";
import format_bytes from "../helpers/format_size.js";

export default {
  name: "ViewNote",
  components: {
    Tag,
    Image,
    ScrollTop,
  },
  props: {
    noteId: {required: true, type: String}
  },
  mounted() {
    api_request.get("/api/notes/"+this.noteId).then(resp => this.noteData = resp.data)
  },
  data() {
    return {
      noteData: null,
    }
  },
  methods: {
    isImage(fileName) {
      return RegExp(/.+\.(png|jpe?g|gif|bpm|svg|ico|tiff)$/i).test(fileName)
    },
    getFileDownloadURL(fileName) {
      return '/api/notes/'+this.noteId+'/files/'+fileName
    },
    formatBytes(size) { return format_bytes(size) },
  }
}
</script>

<style scoped>
.bg-orange-light {
  background-color: #FEAA69;
}
</style>