import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://10.29.29.134',
                changeOrigin: true,
                secure: false,
                ws: true,
            },
            '/media': {target: 'http://10.29.29.134', secure: false},
            '/static': {target: 'http://10.29.29.134', secure: false},
        }
    }
})
