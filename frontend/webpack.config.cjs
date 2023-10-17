const path = require('path')
const { VueLoaderPlugin } = require('vue-loader'); // плагин для загрузки кода Vue

module.exports = {
    entry: {
        login: './src/login.js',
        main: './src/main.js',
        create_update_note: './src/create_update_note.js',
        detail_view_note: './src/detail_view_note.js',
    },
    mode: "production",
    output: {
        path: path.resolve(__dirname, '../static/'),
        publicPath: '/static/',
        filename: '[name].js'
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader'
            },
            {
                test: /\.css$/,
                use: [
                    'style-loader',
                    'css-loader'
                ]
            }
        ]
    },
    plugins: [
        new VueLoaderPlugin()
    ]
}