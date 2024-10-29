<script>
import {defineComponent} from 'vue';
import {component as ckeditor} from '@mayasabha/ckeditor4-vue3';
import {ckeditorConfig, CkeditorImages} from "@/services/ckeditor.ts";

export default defineComponent({
  name: "CKEditorForm",
  components: {ckeditor},
  props: {
    text: {required: true, type: String},
    skipInitialImages: {required: false, type: Boolean, default: false},
  },
  emits: ['update:text'],

  mounted() {
    setTimeout(this.enableImagesAutoResize, 50);
  },

  computed: {
    ckeditorConfig() { return ckeditorConfig },
    value: {
      get() {
        return this.text
      },
      set(value) {
        this.$emit('update:text', value)
      }
    }
  },
  methods: {
    enableImagesAutoResize() {
      // Если режим редактирования, то пропускаем начальные изображения
      const ckeditorImages = new CkeditorImages(this.skipInitialImages);
      ckeditorImages.enableImagesAutoSize();
    }
  }
})
</script>

<template>
  <ckeditor v-model="value" :config="ckeditorConfig" editor-url="/ckeditor/ckeditor.js"></ckeditor>
</template>

<style scoped>

</style>