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
    build: {
        rollupOptions: {
            output: {
                manualChunks(id) {
                    if (id.indexOf('node_modules') !== -1) {
                        return id.toString().split("node_modules/")[1].split("/")[0].toString();
                    }
                }
            }
        }
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                secure: false,
                ws: true,
            },
            '/media': {target: 'http://127.0.0.1:8000', secure: false},
            '/static': {target: 'http://127.0.0.1:8000', secure: false},
        }
    }
})
