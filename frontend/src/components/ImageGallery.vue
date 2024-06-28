<template>
  <div class="text-left">
    <div :id="galleryID"></div>
  </div>
</template>

<script>
import {defineComponent} from 'vue';

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
      galleryID: this.makeID(12)
    }
  },
  mounted() {
    const galleryID = this.galleryID
    let items = []

    this.images.forEach((url, index) => {
      let data = {src: url}
      if (this.withDescriptions) {
        console.log(this.withDescriptions)
        data.title = this.withDescriptions[index]
      }
      items.push(data)
    })

    $(document).ready(function () {
      $(`#${galleryID}`).nanogallery2( {
        // ### gallery settings ###
        thumbnailHeight: 150,
        thumbnailWidth: 150,
        thumbnailL1GutterWidth: 20,
        thumbnailL1GutterHeight: 20,
        thumbnailAlignment: "left",
        thumbnailOpenImage: true,
        thumbnailDisplayTransitionDuration: 1,
        thumbnailDisplayInterval: 1,
        thumbnailBorderVertical: 1,
        thumbnailBorderHorizontal: 1,

        colorScheme: {
          thumbnail: {
            borderColor: "rgba(114,114,114,0.69)",
            borderRadius: "4px",
          }
        },
        thumbnailToolbarImage :  { topLeft: 'display', bottomRight : 'download' },
        allowHTMLinData: true,
        thumbnailLabel: {
          position: "onBottom",
          titleMultiLine: true
        },
        // ### gallery content ###
        items: items
      });
    });
  },

  methods: {
    makeID(length) {
      let result = '';
      const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
      const charactersLength = characters.length;
      let counter = 0;
      while (counter < length) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
        counter += 1;
      }
      return result;
    }
  }
})
</script>

<style scoped>

</style>