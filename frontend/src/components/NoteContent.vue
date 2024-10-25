<template>
  <div id="noteContent" v-html="formatedContent" @contextmenu="onImageRightClick" class="border-300 border-top-1 pt-5"></div>
  <ContextMenu ref="menu" :model="contextMenuItems" @hide="selectedImage = null" />
</template>

<script>
import {defineComponent} from 'vue';
import {getOriginImageURL} from "@/services/thumbnails";
import {nanoGalleryReload} from "@/services/nanogallery";
import {downloadFile} from "@/services/download";

export default defineComponent({
  name: "NoteContent",
  props: {
    content: {required: true, type: String},
    noteId: {required: true, type: String},
  },

  data() {
    return {
      formatedContent: this.formatContent(),
      contextMenuItems: [
        { label: 'Открыть в новом окне', icon: 'pi pi-external-link', command: this.openOriginImage },
        { label: 'Скопировать ссылку', icon: 'pi pi-clipboard', command: this.copyToClipboard },
        { separator: true },
        { label: 'Скачать', icon: 'pi pi-download', command: this.downloadImage },
      ],
      selectedImage: null,
    }
  },

  mounted() {
    nanoGalleryReload()
  },

  methods: {
    onImageRightClick(event) {
      if (event.target.localName === "img") {
        this.$refs.menu.show(event);
        this.selectedImage = event.target.currentSrc;
      }
    },

    copyToClipboard() {
      navigator.clipboard.writeText(getOriginImageURL(this.selectedImage))
    },

    openOriginImage() {
      if (!this.selectedImage) return;
      window.open(getOriginImageURL(this.selectedImage), '_blank')
    },

    downloadImage() {
      if (!this.selectedImage) return;

      // Оригинальное изображение, не превью.
      const originURL = getOriginImageURL(this.selectedImage)

      // Разделяем URL и берем последнюю часть.
      const imageFullName = originURL.split("/").reverse()[0]

      // Имя картинки без UUID вначале, разделяем на 6 частей и берем последнюю.
      const verboseImageName = imageFullName.split("-", 6).reverse()[0]
      downloadFile(originURL, verboseImageName)
    },

    formatContent() {
      const parser = new DOMParser();
      const doc = parser.parseFromString(this.content, 'text/html');

      // Находим все теги <img>
      const images = doc.getElementsByTagName('img');

      // Добавляем атрибуты nanogallery каждому тегу <img>
      for (let i = 0; i < images.length; i++) {
        images[i].toggleAttribute("data-nanogallery2-lightbox")
        images[i].setAttribute('src', images[i].src);

        // Добавляем превью, если имеется.
        images[i].setAttribute('data-ngsrc', getOriginImageURL(images[i].src));

        images[i].setAttribute('data-nanogallery2-lgroup', "note-inline-images-"+this.noteId);
        images[i].style.cssText += "max-width: 100%!important;"
      }

      // Возвращаем измененный HTML как строку
      return doc.documentElement.outerHTML;
    }
  }

})
</script>
