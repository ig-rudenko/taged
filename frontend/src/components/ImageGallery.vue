<template>
  <div class="text-left">
    <div :id="galleryID">
      <div class="flex align-items-center gap-2">
        <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
        <span>Загружаем</span>
      </div>
    </div>
  </div>
</template>

<script>
import {defineComponent} from 'vue';
import {findThumbs, createGallery, makeRandomID} from "@/services/nanogallery";

export default defineComponent({
  name: "ImageGallery",
  props: {
    images: {required: true, type: Array},
    withDescriptions: {
      required: false, type: Array, default: null
    }
  },
  data() {
    return {
      galleryID: makeRandomID(12)
    }
  },
  async mounted() {
    const galleryID = this.galleryID
    const items = await findThumbs(this.images, this.withDescriptions)
    createGallery(galleryID, items)
  },
})
</script>

<style>
tinytext {
  font-size: 0.8rem;
  display: flex;
  justify-content: flex-start;
  width: 140px;
}
</style>