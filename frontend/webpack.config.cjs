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
        filename: '[name]_v1.1.0.js'
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader',
                options: {
                    loaders: {
                        ts: 'ts-loader'
                    },
                    esModule: true
                }
            },
            {
                test: /\.tsx?$/,
                loader: 'ts-loader',
                exclude: /node_modules/,
                options: {
                    appendTsSuffixTo: [/\.vue$/]
                }
            },
            {
                test: /\.js/,
                loader: 'babel-loader'
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            },
            {
                test: /\.s[ac]ss$/i,
                use: [
                    // Creates `style` nodes from JS strings
                    "style-loader",
                    // Translates CSS into CommonJS
                    "css-loader",
                    // Compiles Sass to CSS
                    "sass-loader",
                ],
            }
        ]
    },
    plugins: [
        new VueLoaderPlugin()
    ],
    resolve: {
        extensions: ['.tsx', '.ts', '.js']
    },
    performance: {
        maxEntrypointSize: 712000,
        maxAssetSize: 712000
   },
}