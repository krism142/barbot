// Mock axios module to avoid ESM issues
jest.mock('axios', () => {
  return {
    post: jest.fn(),
    get: jest.fn(),
    create: jest.fn(),
    defaults: {
      adapter: 'xhr'
    }
  }
})
