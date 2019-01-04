const path = require('path');

module.exports = {
  configureWebpack: {
    resolve: {
      alias: {
        '@store': path.join(__dirname, '/src/store'),
        '@helpers': path.join(__dirname, '/src/helpers'),
        '@components': path.join(__dirname, '/src/components')
      }
    }
  },

  pluginOptions: {
    s3Deploy: {
      awsProfile: 'default',
      region: 'us-east-1',
      bucket: 'cse6242-t2-frontend',
      createBucket: false,
      staticHosting: true,
      staticIndexPage: 'index.html',
      staticErrorPage: 'error.html',
      assetPath: 'dist',
      assetMatch: '**',
      deployPath: '/',
      acl: 'public-read',
      pwa: false,
      enableCloudfront: true,
      cloudfrontId: 'E1Q3LO3M5WTN4N',
      cloudfrontMatchers: '/*',
      uploadConcurrency: 5,
      pluginVersion: '3.0.0'
    }
  }
}
