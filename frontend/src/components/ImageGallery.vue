<template>
  <div class="text-left">
    <div :id="galleryID"></div>
  </div>
</template>

<script>
import {defineComponent} from 'vue';
import {getSmallThumbnail, hasSmallThumbnail} from "@/services/thumbnails";

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
  async mounted() {
    const galleryID = this.galleryID
    let items = []

    for (const url of this.images) {
      const index = this.images.indexOf(url);
      let data = {src: url}
      if (await hasSmallThumbnail(url)) {
        data.srct = getSmallThumbnail(url)
      }

      if (this.withDescriptions) {
        data.title = this.withDescriptions[index]
      }
      items.push(data)
    }

    $(document).ready(function () {
      $(`#${galleryID}`).nanogallery2( {
        // ### gallery settings ###
        thumbnailHeight: 150,
        thumbnailWidth: 150,
        thumbnailL1GutterWidth: 20,
        thumbnailL1GutterHeight: 20,
        blurredImageQuality: 3,
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

<style>
tinytext {
  font-size: 0.8rem;
  display: flex;
  justify-content: flex-start;
  width: 140px;
}
</style>