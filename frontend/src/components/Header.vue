<template>
  <div>
    <div class="header-image"></div>
    <div class="px-4 py-5 md:px-6 lg:px-8 surface-section">
      <div class="flex-column lg:flex-row lg:align-items-center lg:justify-content-between relative" style="margin-top: -2rem; top: -70px; margin-bottom: -70px;">
        <div>
          <div class="menu-card">
            <div class="flex lg:align-items-center">
              <a href="/" class="mb-3 mr-2 flex align-items-center justify-content-center knowledge-button cursor-pointer">
                <img class="knowledge-button" src="/static/img/note.svg" alt="Image">
              </a>
              <div class="align-items-center border-round-2xl flex justify-content-center library-button mb-3">
                  <img :src="'/static/images/cat'+getRandomInt(0, 8)+'.gif'" alt="Image" width="120" height="120">
              </div>
            </div>

            <div v-if="showCount" class="flex flex-wrap">
              <div class="p-3 mr-2 w-10rem text-center bg-indigo-500 shadow-2" style="border-radius: 12px;">
                <span class="inline-flex justify-content-center align-items-center bg-indigo-600 border-circle mb-3 p-3">
                  <i class="pi pi-file text-xl text-white"></i>
                </span>
                <div class="text-2xl font-medium text-white mb-2">{{ totalCount }}</div>
                <span class="text-indigo-100 font-medium">Записей</span>
              </div>
            </div>

          </div>
          <div class="pt-4 text-900 text-3xl font-medium mb-3">{{ sectionName }}</div>
          <p class="mt-0 mb-3 text-700 text-xl">{{ sectionDescription }}</p>
        </div>
        <Button v-if="showCreateButton" @click="goToCreateNoteURL" rounded label="Создать" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Button from "primevue/button/Button.vue";
import api_request from "../api_request";

export default {
  name: "Header",
  components: {
    Button,
  },
  props: {
    showCount: {required: false, default: true, type: Boolean},
    sectionName: {required: true, type: String},
    sectionDescription: {required: false, default: "", type: String},
    showCreateButton: {required: false, default: false, type: Boolean},
  },
  data() {
    return {
      totalCount: 0
    }
  },
  mounted() {
    if (this.showCount) {
      this.getTotalRecordsCount()
    }
  },
  methods: {
    getTotalRecordsCount(): void {
      api_request.get("/api/notes/count").then(resp => this.totalCount = resp.data.totalCount)
    },
    goToCreateNoteURL(): void {
      window.location.href = "/notes/create"
    },
    getRandomInt(min: number, max: number): number {
      min = Math.ceil(min);
      max = Math.floor(max);
      return Math.floor(Math.random() * (max - min + 1)) + min;
    },
  }

}
</script>

<style scoped>
.header-image {
  height: 200px;
  background-image: url('/static/img/knowledge-background.png');
  background-position: center;
}

.knowledge-button {
  width: 140px;
  height: 140px;
  border-radius: 10px;
}

.knowledge-button:hover {
  transform: scale(1.04);
}

.library-button {
  width: 120px;
  height: 120px;
  border-radius: 10px;
}

.library-button:hover {
  transform: scale(1.04);
}

.menu-card {
  display: flex;
  flex-wrap: wrap;
  -webkit-box-pack: justify!important;
  -ms-flex-pack: justify!important;
  justify-content: space-between!important;
}

@media (max-width: 500px) {
  .menu-card {
    -webkit-box-pack: center!important;
    -ms-flex-pack: center!important;
    justify-content: center!important;
  }
}


</style>