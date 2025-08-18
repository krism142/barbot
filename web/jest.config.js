module.exports = {
  transformIgnorePatterns: [
    '/node_modules/(?!axios)/'
  ],
  setupFilesAfterEnv: [
    '<rootDir>/src/setupJest.js'
  ]
}
