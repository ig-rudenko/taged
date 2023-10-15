<template>
  <div>
    <div class="header-image"></div>
    <div class="px-4 py-5 md:px-6 lg:px-8 surface-section">
      <div class="flex-column lg:flex-row lg:align-items-center lg:justify-content-between relative" style="margin-top: -2rem; top: -70px; margin-bottom: -70px;">
        <div>
          <div class="flex flex-wrap justify-content-between">
            <div class="flex lg:align-items-center">
              <div class="mb-3 mr-2 surface-card shadow-2 flex align-items-center justify-content-center knowledge-button cursor-pointer">
                <img class="knowledge-button" src="/static/img/digital-brain.png" alt="Image">
              </div>
              <div class="mb-3 surface-card shadow-2 flex align-items-center justify-content-center library-button cursor-pointer">
                <!--            <img src="images/blocks/logos/hyper.svg" alt="Image" width="70" height="70">-->
              </div>
            </div>

            <div class="flex flex-wrap">
              <div class="p-3 mr-2 w-10rem text-center bg-purple-400 shadow-2" style="border-radius: 12px;">
              <span class="inline-flex justify-content-center align-items-center bg-purple-500 border-circle mb-3 p-3">
                <i class="pi pi-file text-xl text-white"></i>
              </span>
                <div class="text-2xl font-medium text-white mb-2">{{ totalCount }}</div>
                <span class="text-indigo-100 font-medium">Записей</span>
              </div>
            </div>

          </div>
          <div class="text-900 text-3xl font-medium mb-3">База знаний</div>
          <p class="mt-0 mb-3 text-700 text-xl">Здесь вы можете найти необходимую для вас информацию</p>
        </div>
        <Button rounded label="Создать" />
      </div>
    </div>
  </div>
</template>

<script>
import "/src/assets/header.css"
import Button from "primevue/button/Button.vue";
import api_request from "../api_request.js";

export default {
  name: "Header",
  components: {
    Button,
  },
  data() {
    return {
      totalCount: 0
    }
  },
  mounted() {
    this.getTotalRecordsCount()
  },
  methods: {
    getTotalRecordsCount() {
      api_request.get("/api/notes/count").then(resp => this.totalCount = resp.data.totalCount)
    }
  }

}
</script>

<style scoped>
.header-image {
  height: 200px;
  background-image: url('/static/img/knowledge-background.png');
  background-repeat: no-repeat;
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

</style>