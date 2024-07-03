// craco.config.js
const CracoLessPlugin = require('craco-less');
const dotenv = require('dotenv');

dotenv.config({
    path: `.env.${process.env.NODE_ENV}.local`
});

module.exports = {
    plugins: [
        {
            plugin: CracoLessPlugin,
            options: {
                lessLoaderOptions: {
                    lessOptions: {
                        javascriptEnabled: true,
                    },
                },
            },
        },
    ],
};
