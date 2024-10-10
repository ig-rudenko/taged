<template>
  <div v-if="noteImages.length > 0" class="mb-3">
    <div class="flex justify-content-start">
      <Button @click="toggle" class="text-right cursor-pointer border-1" size="small" outlined>
        <span class="mr-1">Изображения в тексте</span>
        <i :class="['pi', show?'pi-angle-up':'pi-angle-down']"/>
      </Button>
    </div>

    <div v-if="loaded" v-show="show" class="p-2 bg-black-alpha-10 border-round">
      <ImageGallery :images="noteImages"/>
    </div>
  </div>
</template>

<script lang="ts">
import {defineComponent} from 'vue'
import ImageGallery from "@/components/ImageGallery.vue";
import {getOriginImageURL} from "@/services/thumbnails";

export default defineComponent({
  name: "InTextImages",
  components: {ImageGallery},
  props: {
    text: {required: true, type: String},
  },
  data() {
    return {
      loaded: false,
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
      if (match) match.forEach(value => {
        this.noteImages.push(getOriginImageURL(value))
      })
    },

    toggle() {
      this.loaded = true;
      this.show = !this.show
    }
  }
})
</script>

<style scoped>

</style>