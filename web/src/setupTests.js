// jest-dom adds custom jest matchers for asserting on DOM nodes.
import '@testing-library/jest-dom';
import { server } from './tests/mocks/server';

// Establish API mocking before all tests
beforeAll(() => server.listen());

// Reset any request handlers between tests
afterEach(() => server.resetHandlers());

// Clean up after the tests are finished
afterAll(() => server.close());