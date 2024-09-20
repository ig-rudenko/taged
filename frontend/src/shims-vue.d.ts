// shims-vue.d.ts
import { Router, RouteLocation } from 'vue-router'

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $router: Router;
    $route: RouteLocation;
  }
}
