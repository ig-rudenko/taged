<template>
  <div v-if="noteImages.length > 0" class="mb-3">
    <div class="flex justify-content-start">
      <Button @click="show=!show" class="text-right cursor-pointer border-1" size="small" outlined>
        <span class="mr-1">Изображения в тексте</span>
        <i :class="['pi', show?'pi-angle-up':'pi-angle-down']"/>
      </Button>
    </div>

    <div v-if="show" class="p-2 bg-black-alpha-10 border-round">
      <ImageGallery :images="noteImages"/>
    </div>
  </div>
</template>

<script lang="ts">
import Image from "primevue/image/Image.vue";
import {defineComponent} from 'vue'
import ImageGallery from "@/components/ImageGallery.vue";

export default defineComponent({
  name: "InTextImages",
  components: {ImageGallery, Image},
  props: {
    text: {required: true, type: String},
  },
  data() {
    return {
      show: false,
      noteImages: [] as string[]
    }
  },

  mounted() {
    this.findImagesInNote()
  },

  methods: {
    findImagesInNote() {
      const match = this.text.match(/(?<=<img.*? src=")\S+?(?=")/gi)
      if (match) match.forEach(value => this.noteImages.push(value))
    },
  }
})
</script>

<style scoped>

</style>