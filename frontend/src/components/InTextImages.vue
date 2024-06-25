<template>
  <div v-if="noteImages.length > 0" class="mb-3">
    <div class="flex justify-content-start">
      <Button @click="show=!show" class="text-right cursor-pointer border-1" size="small" outlined>
        <span class="mr-1">Изображения в тексте</span>
        <i :class="['pi', show?'pi-angle-up':'pi-angle-down']"/>
      </Button>
    </div>
    <div v-if="show" class="flex flex-wrap justify-content-start">
      <div v-for="url in noteImages" class="flex align-items-center">
        <Image :src="url" preview class="rounded-3 p-2" :image-style="{'max-height': '168px!important', 'max-width': '168px!important'}" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Image from "primevue/image/Image.vue";
import {defineComponent} from 'vue'

export default defineComponent({
  name: "InTextImages",
  components: {Image},
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