<template>

  <div id="drag-drop-area">
    <div class="col-md-auto">
      <div class="file-upload align-items-end">

        <div>
          <label class="py-3" for="file-input">
            <span class="cursor-pointer flex align-items-center mb-4 hover:text-indigo-500">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="mr-2"
                   viewBox="0 0 16 16">
                <path
                    d="M8 6.5a.5.5 0 0 1 .5.5v1.5H10a.5.5 0 0 1 0 1H8.5V11a.5.5 0 0 1-1 0V9.5H6a.5.5 0 0 1 0-1h1.5V7a.5.5 0 0 1 .5-.5z"/>
                <path
                    d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z"/>
              </svg>
              <span>Добавить файл</span>
            </span>

          </label>
          <input hidden id="file-input" multiple type="file" @change="handleFileChange"/>
        </div>

        <div class="flex flex-wrap align-items-center">

          <div v-for="(file_obj, index) in files" :key="index" class="m-2 w-17rem">
            <div class="flex align-items-end flex-column">
              <i @click="deleteFile(index)"
                 class="pi pi-times border-round-2xl border-1 px-1 py-1 cursor-pointer hover:text-red-500"
                 aria-label="Cancel"/>
              <MediaPreview :file="file_obj" :is-file-object="true" :max-file-name-length="20"/>
            </div>
          </div>

        </div>
      </div>


    </div>
  </div>

</template>

<script lang="ts">
import MediaPreview from "@/components/MediaPreview.vue";

export default {
  name: "LoadMedia",
  components: {
    MediaPreview,
  },
  emits: ["selectedFiles", "change"],

  data() {
    return {
      files: [] as File[]
    }
  },

  mounted() {
    this.addDragAndDropListeners()
  },

  methods: {

    addDragAndDropListeners(): void {
      let container: Element = document.querySelector("#drag-drop-area")!;
      container.addEventListener("dragover", e => e.preventDefault());
      container.addEventListener("drop", (e) => this.addByDragAndDrop(<DragEvent>e));
    },

    addByDragAndDrop(e: DragEvent): void {
      e.preventDefault();
      if (e.dataTransfer?.files) this.addFiles(e.dataTransfer.files);
    },

    handleFileChange(event: Event): void {
      const files = (<HTMLInputElement>event.target).files
      if (files) this.addFiles(files);
    },

    addFiles(files: FileList): void {
      this.files = [...Array.from(files), ...this.files]
      this.$emit("selectedFiles", this.files)
    },

    deleteFile(index: number): void {
      this.files.splice(index, 1)
      this.$emit("change", this.files)
    },

  }
}
</script>

<style scoped>
.file-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>