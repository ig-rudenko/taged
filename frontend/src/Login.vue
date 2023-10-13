<template id="app" >
  <div class="back form-signin">
    <div class="panel">

      <div>
        <img src="/static/img/login-logo.svg" alt="login-logo">
      </div>

      <div class="welcome-panel">
        <h3 class="welcome-text">Добро пожаловать в Базу Знаний</h3>

        <form class="form" method="post">
          <input hidden name="csrfmiddlewaretoken" :value="csrfMiddlewareToken">
          <div class="py-3 w-100">
            <InputText name="username" class="w-100" autofocus v-model.trim="login" placeholder="Логин"/>
          </div>
          <div class="py-3 w-100">
            <InputText name="password" class="w-100" v-model.trim="password" type="password" placeholder="Пароль"/>
          </div>
          <div class="py-3">
            <Button label="Войти" type="submit" severity="primary" />
          </div>
        </form>

        <div class="end-block">
          <div style="margin-right: 0.25rem;">ig-rudenko &copy; 2021-2023</div>
          <div>
            <a href="https://www.elastic.co/elasticsearch/" target="_blank" title="Elasticsearch">
              <img src="https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt36f2da8d650732a0/5d0823c3d8ff351753cbc99f/logo-elasticsearch-32-color.svg"
                   alt="elasticsearch" width="32" height="32"/>
            </a>

            <a href="https://github.com/ig-rudenko/taged" target="_blank" title="GitHub">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 16 16">
                <circle fill="white" cx="8" cy="8" r="7.8"></circle>
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import InputText from "primevue/inputtext";
import Button from "primevue/button";

export default {
  app: "Login",
  components: {
    InputText,
    Button,
  },
  data(){
    return {
      login: "",
      password: "",
      csrfMiddlewareToken: "",
    }
  },
  mounted() {
    const tokenItem = document.querySelector("input[name=csrfmiddlewaretoken]")
    this.csrfMiddlewareToken = tokenItem?tokenItem.value:""
  }
}
</script>

<style scoped>

.back {
  display: flex;
  margin: 0 auto;
}

.panel {
  position: relative;
  top: -80px;
  padding: 0 5rem 0 5rem;
  border-radius: 20px;
  margin: 0 auto;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.welcome-panel {
  position: relative;
  top: -6rem;
}

.welcome-text {
  text-align: center;
}

.w-100 {
  width: 100%;
  margin: 0 auto;
}

.py-3 {
  padding-top: 0.3rem;
  padding-bottom: 0.3rem;
}

.form {
  display: flex;
  flex-wrap: wrap;
}

.end-block {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  font-size: 12px;
}


@media (max-width: 768px) {
  .panel {
    padding: 0 25px 25px 25px;
    box-shadow: none;
    top: -50px;
  }
  .welcome-panel {
    top: -4rem;
  }
}

</style>