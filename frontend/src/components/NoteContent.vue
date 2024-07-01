<template>
  <div id="noteContent" v-html="formatedContent" class="border-300 border-top-1 pt-5"></div>
</template>

<script>
import {defineComponent} from 'vue';

export default defineComponent({
  name: "NoteContent",
  props: {
    content: {required: true, type: String}
  },

  data() {
    return {
      formatedContent: this.formatContent()
    }
  },

  mounted() {
    import("../../public/js/jquery@3.1.0.min.js")
    import("../../public/js/nanogallery2.min.js")
  },

  methods: {

    formatContent() {
      const parser = new DOMParser();
      const doc = parser.parseFromString(this.content, 'text/html');

      // Находим все теги <img>
      const images = doc.getElementsByTagName('img');

      // Добавляем атрибут data-new="gg" каждому тегу <img>
      for (let i = 0; i < images.length; i++) {
        // images[i].setAttribute('data-nanogallery2-lightbox', '');
        images[i].toggleAttribute("data-nanogallery2-lightbox")
        images[i].setAttribute('data-ngsrc', images[i].src);
        images[i].setAttribute('data-nanogallery2-lgroup', "inline-content");
      }

      // Возвращаем измененный HTML как строку
      return doc.documentElement.outerHTML;
    }
  }

})
</script>

<style scoped>

</style>