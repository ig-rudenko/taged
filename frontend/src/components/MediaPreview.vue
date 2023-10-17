<template>
  <!--Предпросмотр изображения-->
  <div class="flex align-items-center align-self-center">
    <Image v-if="isImage" preview :image-style="{'max-height': '64px', 'max-width': '64px'}"
           class="rounded-3 mr-2" :src="imageSrc" alt="Предпросмотр изображения"/>

    <img v-else height="48" class="mr-2" :src="'/static/images/icons/'+fileFormat+'.png'" :alt="file.name">

    <div class="flex flex-column">
      <span v-if="isFileObject">{{shortenString(file.name)}}</span>
      <a v-else :href="getFileDownloadLink()" class="text-900 no-underline hover:text-indigo-500">{{shortenString(file.name)}}</a>
      <span class="font-normal text-500">{{formatBytes(file.size)}}</span>
    </div>
  </div>
</template>

<script>
import Image from "primevue/image/Image.vue";
import format_bytes from "../helpers/format_size.js";

export default {
  name: "MediaPreview",
  components: {
    Image,
  },
  props: {
    file: {required: true},
    isFileObject: {required: true},
    fileNoteID: {required: false, default: null},
  },
  data() {
    return {
      currentFile: null,
      isImage: false,
      imageSrc: ""
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
  },

  computed: {
    fileFormat() {
      if (this.file.name.match(/.+\.(docx?|rtf)$/i)){
        return 'docx'
      }
      if (this.file.name.match(/.+\.xls[xm]?$/i)){
        return 'xlsx'
      }
      if (this.file.name.match(/.+\.pdf$/i)){
        return 'pdf'
      }
      if (this.file.name.match(/.+\.xml$/i)){
        return 'xml'
      }
      if (this.file.name.match(/.+\.drawio$/i)){
        return 'drawio'
      }
      if (this.file.name.match(/.+\.txt$/i)){
        return 'txt'
      }
      if (this.file.name.match(/.+\.vsdx?$/i)){
        return 'visio'
      }
      if (this.file.name.match(/.+\.(png|jpe?g|gif|bpm|svg|ico|tiff)$/i)){
        return 'img'
      }
      if (this.file.name.match(/.+\.(rar|7z|zip|tar[.gz]|iso)$/i)){
        return 'archive'
      }
        return 'file'
    }
  },

  methods: {
    shortenString(str) {
      const limit = 15
      // Проверяем, что строка длиннее лимита
      if (str.length > limit) {
        // Вычисляем, сколько символов нужно оставить с каждого края
        let edge = Math.floor((limit - 3) / 2);
        // Возвращаем новую строку с троеточием посередине
        return str.slice(0, edge) + "..." + str.slice(-edge);
      } else {
        // Возвращаем исходную строку без изменений
        return str;
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
        this.imageSrc = this.getFileDownloadLink()
      }
    },

    getFileDownloadLink() {
      return '/api/notes/'+this.fileNoteID+'/files/'+this.file.name
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