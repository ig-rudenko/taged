<template>
  <!--Предпросмотр изображения-->
  <div class="flex align-items-center align-self-center">
    <Image v-if="isImage" preview :image-style="{'max-height': '64px', 'max-width': '64px'}"
           class="rounded-3 mr-2" :src="imageSrc" alt="Предпросмотр изображения"/>

    <img @click="enterFile" v-else height="48" class="mr-2 cursor-pointer" :src="fileIconURL" :alt="file.name">

    <div class="flex flex-column">
      <span @click="enterFile" class="text-900 hover:text-indigo-500 cursor-pointer">{{shortenString(file.name)}}</span>
      <span class="font-normal text-500">
        {{formatBytes(file.size)}}
        <a v-if="!isFileObject" target="_blank" :href="fileDownloadLink" class="ml-1">
          <i class="pi pi-download cursor-pointer font-bold text-700 hover:text-indigo-500" />
        </a>
      </span>
    </div>
  </div>

  <Dialog v-model:visible="showFilePreviewModal" :header="file.name" modal :show-header="true" style="max-height: 100%"
          :style="{ width: '100vw', height: '100%' }">
    <object type="application/pdf" :data="fileOriginLink" :title="file.name" width="100%" :height="windowHeight"></object>
  </Dialog>


</template>

<script>
import Dialog from "primevue/dialog/Dialog.vue";
import Image from "primevue/image/Image.vue";

import format_bytes from "../helpers/format_size.js";
import getFileFormatIconName from "../helpers/icons.js";

export default {
  name: "MediaPreview",
  components: {
    Dialog,
    Image,
  },
  props: {
    file: {required: true},
    isFileObject: {required: true},
    fileNoteID: {required: false, default: null},
    maxFileNameLength: {required: false, default: null},
  },
  data() {
    return {
      currentFile: null,
      isImage: false,
      imageSrc: "",
      showFilePreviewModal: false,
      windowHeight: window.innerHeight,
    }
  },
  mounted() {
    this.checkFile()
    this.currentFile = this.file
  },
  updated() {
    if (this.currentFile !== this.file){
      this.currentFile = this.file
      this.checkFile()
    }
    window.addEventListener("reset", () => this.windowHeight = window.innerHeight)
  },

  computed: {
    fileIconURL() {
      const icon = getFileFormatIconName(this.file.name)
      return'/static/images/icons/' + icon + '.png'
    },
    fileDownloadLink() {
      return '/api/notes/'+this.fileNoteID+'/files/'+this.file.name
    },
    fileOriginLink() {
      return '/media/'+this.fileNoteID+'/'+this.file.name
    },

  },

  methods: {
    shortenString(str) {
      if (!this.maxFileNameLength) return str;

      // Проверяем, что строка длиннее лимита
      if (str.length > this.maxFileNameLength) {
        // Вычисляем, сколько символов нужно оставить с каждого края
        let edge = Math.floor((this.maxFileNameLength - 3) / 2);
        // Возвращаем новую строку с троеточием посередине
        return str.slice(0, edge) + "..." + str.slice(-edge);
      } else {
        // Возвращаем исходную строку без изменений
        return str;
      }
    },

    enterFile() {
      if (this.file.name.endsWith(".pdf")) {
        this.showFilePreviewModal = true
      }
    },

    checkFile() {
      if (this.isFileObject) {
        this.isImage = this.file.type.startsWith("image/");
        if (this.isImage) {
          // Создать URL-адрес объекта для предварительного просмотра изображения
          this.imageSrc = URL.createObjectURL(this.file);
        }
      } else {
        this.isImage = RegExp(/.+\.(png|jpe?g|gif|bpm|svg|ico|tiff)$/i).test(this.file.name)
        this.imageSrc = this.fileOriginLink
      }
    },

    formatBytes(size) { return format_bytes(size) },
  }
}
</script>

<style scoped>
img {
  max-width: 100%;
}
</style>