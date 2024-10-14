<template>
  <div id="noteContent" v-html="formatedContent" class="border-300 border-top-1 pt-5"></div>
</template>

<script>
import {defineComponent} from 'vue';
import {getOriginImageURL} from "@/services/thumbnails";
import {nanoGalleryReload} from "@/services/nanogallery";

export default defineComponent({
  name: "NoteContent",
  props: {
    content: {required: true, type: String},
    noteId: {required: true, type: String},
  },

  data() {
    return {
      formatedContent: this.formatContent()
    }
  },

  mounted() {
    nanoGalleryReload()
  },

  methods: {
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
