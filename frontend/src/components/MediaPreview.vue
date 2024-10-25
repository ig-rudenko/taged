<template>
  <!--Предпросмотр изображения-->
  <div class="flex align-items-center align-self-center gap-2 h-full">
    <img v-if="isImage" :src="imageThumbnail" alt="" :style="imageStyles" class="hover:border-600 hover:shadow-2 cursor-pointer"
         :data-ngsrc="getOriginImageURL(imageSrc)" :data-nanogallery2-lgroup="nggroup" data-nanogallery2-lightbox>

    <img v-else @click="enterFile" :style="iconStyles" class="mr-2 cursor-pointer" :src="fileIconURL" :alt="file.name">

    <div class="flex flex-column">
      <span @click="enterFile" :title="file.name"
            class="text-900 hover:text-indigo-500 cursor-pointer">{{ shortenString(file.name) }}</span>
      <span class="font-normal text-500">
        {{ formatBytes(file.size) }}
        <span v-if="!isFileObject" @click="download" class="ml-1">
          <i class="pi pi-download cursor-pointer font-bold text-700 hover:text-indigo-500"/>
        </span>
      </span>
    </div>
  </div>

  <Dialog v-model:visible="showFilePreviewModal" modal :show-header="true" style="max-height: 100%"
          :style="{ width: '100vw', height: '100%' }">
    <object type="application/pdf" :data="fileOriginLink" :title="file.name" width="100%"
            :height="windowHeight">
      <div class="p-4" style="height: 50vh;">Ваш браузер не поддерживает просмотр pdf документов через модальное окно</div>
    </object>
  </Dialog>


</template>

<script lang="ts">
import {PropType} from "vue";

import {NoteFile} from "@/note";
import format_bytes from "@/helpers/format_size";
import getFileFormatIconName from "@/helpers/icons";
import {getOriginImageURL, getSmallThumbnailIfHas} from "@/services/thumbnails";
import {makeRandomID, nanoGalleryReload} from "@/services/nanogallery";
import {downloadFile} from "@/services/download.ts";

export default {
  name: "MediaPreview",
  props: {
    file: {required: true, type: Object as PropType<NoteFile | File>},
    isFileObject: {required: true, type: Boolean},
    fileNoteID: {required: false, default: null, type: String},
    maxFileNameLength: {required: false, default: -1, type: Number},
    nggroup: {required: false, type: String, default: makeRandomID(10)},
  },
  data() {
    return {
      currentFile: null as NoteFile | File | null,
      isImage: false,
      imageSrc: "",
      imageThumbnail: "",
      showFilePreviewModal: false,
      windowHeight: window.innerHeight,
    }
  },
  mounted() {
    this.checkFile();
    this.currentFile = this.file;
    nanoGalleryReload()
  },

  updated() {
    if (this.currentFile !== this.file) {
      this.currentFile = this.file
      this.checkFile()
    }
    window.addEventListener("reset", () => this.windowHeight = window.innerHeight)
  },

  computed: {
    fileIconURL(): string {
      const icon = getFileFormatIconName(this.file.name)
      return '/icons/formats/' + icon + '.png'
    },
    fileDownloadLink(): string {
      return '/notes/' + this.fileNoteID + '/files/' + this.file.name
    },
    fileOriginLink(): string {
      return '/media/' + this.fileNoteID + '/' + this.file.name
    },
    imageStyles() {
      return {'max-height': '96px!important', 'max-width': '96px!important'}
    },
    iconStyles() {
      return {'max-height': '48px!important', 'max-width': '48px!important'}
    }
  },

  methods: {
    getOriginImageURL,

    shortenString(str: string): string {
      if (this.maxFileNameLength == -1) return str;

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

    download() {
      downloadFile(this.fileDownloadLink, this.file.name)
    },

    enterFile(): void {
      if (this.file.name.endsWith(".pdf")) {
        this.showFilePreviewModal = true
      }
    },

    checkFile(): void {
      if (this.isFileObject) {
        this.isImage = this.file.type.startsWith("image/");
        if (this.isImage) {
          // Создать URL-адрес объекта для предварительного просмотра изображения
          this.imageSrc = URL.createObjectURL((<Blob>this.file));
        }
      } else {
        const isImage = RegExp(/.+\.(png|jpe?g|gif|bpm|svg|ico|tiff)$/i).test(this.file.name);
        this.imageSrc = this.fileOriginLink;
        if (isImage) {
          getSmallThumbnailIfHas(this.imageSrc).then(value => {
            this.imageThumbnail = value;
            this.isImage = true;
          })
        }
      }
    },

    formatBytes(size: number): string {
      return format_bytes(size)
    },
  }
}
</script>

<style scoped>
img {
  max-width: 100%;
}
</style>