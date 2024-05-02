<template id="app">
  <div class="back form-signin">
    <div class="panel">

      <div class="flex justify-content-center">
        <img height="450px" src="/img/login-logo.svg" alt="login-logo">
      </div>

      <div class="welcome-panel">
        <h3 class="welcome-text pt-2">Добро пожаловать в Базу Знаний</h3>

        <div>
          <div v-if="userError.length" class="flex justify-content-center">
            <InlineMessage @click="userError = ''" severity="error"><span v-html="userError"></span></InlineMessage>
          </div>
          <div class="py-3 w-100">
            <InputText @keydown.enter="handleLogin" name="username" class="w-100" autofocus v-model="user.username"
                       placeholder="Логин"/>
          </div>
          <div class="py-3 w-100">
            <InputText @keydown.enter="handleLogin" name="password" class="w-100" v-model="user.password"
                       type="password" placeholder="Пароль"/>
          </div>
          <div class="py-3">
            <Button @click="handleLogin" label="Войти" type="submit" severity="primary"/>
          </div>
        </div>

        <div class="end-block">
          <div style="margin-right: 0.25rem;">ig-rudenko &copy; 2021-{{ (new Date()).getFullYear() }}</div>
          <div>
            <a href="https://www.elastic.co/elasticsearch/" target="_blank" title="Elasticsearch">
              <img class="icon" src="/icons/elasticsearch.svg" alt="elasticsearch"/>
            </a>
            <a href="https://github.com/ig-rudenko/taged" target="_blank" title="GitHub">
              <img class="icon" src="/icons/github.svg" alt="github"/>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import {mapActions, mapState} from "vuex";
import {AxiosError, AxiosResponse} from "axios";

import {LoginUser} from "@/user";
import {getVerboseAxiosError} from "@/errorFmt";

export default {
  app: "Login",
  data() {
    return {
      user: new LoginUser(),
      userError: "",
    };
  },
  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
    }),
  },
  created() {
    document.title = "Вход в Базу Знаний"
    if (this.loggedIn) this.$router.push("/");
  },
  methods: {
    ...mapActions("auth", ["login"]),

    handleLogin() {
      this.login(this.user)
          .then(
              (value: AxiosResponse | AxiosError) => {
                if (value.status == 200) {
                  this.$router.push("/");
                } else {
                  this.userError = getVerboseAxiosError((<AxiosError>value))
                }
              },
              () => this.userError = 'Неверный логин или пароль'
          )
          .catch(
              (reason: AxiosError<any>) => {
                this.userError = getVerboseAxiosError(reason)
              }
          );
    },

  },
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

.end-block {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  font-size: 12px;
}

.icon {
  width: 32px !important;
  height: 32px !important;
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