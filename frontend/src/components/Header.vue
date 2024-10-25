<template>
  <div>
    <div class="header-image"></div>
    <div class="px-4 md:px-6 lg:px-8 surface-section">
      <div class="flex-column lg:flex-row lg:align-items-center lg:justify-content-between relative"
           style="margin-top: -2rem; top: -70px; margin-bottom: -70px;">
        <div>
          <div class="menu-card">
            <div class="flex lg:align-items-center">
              <a href="/"
                 class="mb-3 mr-2 flex align-items-center justify-content-center knowledge-button cursor-pointer">
                <img class="knowledge-button" src="/img/note.svg" alt="Image">
              </a>
              <div class="align-items-center border-round-2xl flex justify-content-center library-button mb-3">
                <img :src="'/img/cats/cat'+getRandomInt(0, 8)+'.gif'" alt="Image" width="120" height="120">
              </div>
            </div>

            <div v-if="showCount" class="flex flex-wrap h-full">
              <div id="notesCountBlock" class="border-round-2xl align-items-center bg-indigo-500 flex flex-column sm:p-5 gap-2 shadow-2 text-center">
                <div class="flex align-items-center gap-2">
                  <i class="pi pi-file sm:text-3xl text-white"></i>
                  <div class="sm:text-2xl font-medium text-white">{{ totalCount }}</div>
                </div>
                <span class="text-indigo-100 sm:font-medium">Записей</span>
              </div>
            </div>

          </div>
          <div class="text-900 text-4xl font-medium my-3 sm:mt-0">{{ sectionName }}</div>
        </div>
        <Button v-if="showCreateButton" @click="goToCreateNoteURL" icon="pi pi-book" rounded label="Создать"/>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import api from "@/services/api";
import {mapState} from "vuex";

export default {
  name: "Header",
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
    if (!this.loggedIn) this.$router.push('/login');
    if (this.showCount) {
      this.getTotalRecordsCount()
    }
  },
  computed: {
    ...mapState({loggedIn: (state: any) => state.auth.status.loggedIn}),
  },
  methods: {
    getTotalRecordsCount(): void {
      api.get("/notes/count").then(resp => this.totalCount = resp.data.totalCount)
    },
    goToCreateNoteURL(): void {
      this.$router.push("/notes/create")
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
  background-image: url('/img/knowledge-background.png');
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
  -webkit-box-pack: justify !important;
  -ms-flex-pack: justify !important;
  justify-content: space-between !important;
  align-items: center;
}

@media (max-width: 500px) {
  .menu-card {
    -webkit-box-pack: center !important;
    -ms-flex-pack: center !important;
    justify-content: center !important;
  }

  #notesCountBlock {
    flex-direction: row!important;
    width: 100%!important;
    padding: 1rem!important;
  }
}


</style>