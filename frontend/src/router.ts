import {createRouter, createWebHistory, Router, RouteRecordRaw} from "vue-router";

import Login from "@/pages/Login.vue";
import Notes from "@/pages/Notes.vue";
import CreateUpdateNote from "@/pages/CreateUpdateNote.vue";
import DetailViewNote from "@/pages/DetailViewNote.vue";
import ShareNoteView from "@/pages/ShareNoteView.vue";


const routes: RouteRecordRaw[] = [
    {path: "/", component: Notes},
    {path: "/login", component: Login},
    {path: "/notes/create", component: CreateUpdateNote},
    {path: "/notes/:id/edit", component: CreateUpdateNote},
    {path: "/notes/:id", component: DetailViewNote},
    {path: "/temp/:token", component: ShareNoteView},
]

const router: Router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;