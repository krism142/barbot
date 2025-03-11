import React from 'react'
import { render, screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import axios from 'axios'
import { AuthProvider, useAuth } from '/context/AuthContext'

// Mock axios
jest.mock('axios')

// Simple component that uses the auth context
const TestComponent = () => {
  const { user, login, logout, register, isAuthenticated, error, loading } = useAuth()
  
  return (
    <div>
      {isAuthenticated ? (
        <>
          <div data-testid="user-info">
            {user?.username  'No user'}
          </div>
          <button data-testid="logout-button" onClick={logout}>
            Logout
          </button>
        </>
      ) : (
        <>
          <div data-testid="auth-status">Not authenticated</div>
          <button 
            data-testid="login-button" 
            onClick={() => login('testuser', 'password')}
          >
            Login
          </button>
          <button 
            data-testid="register-button" 
            onClick={() => register({
              username: 'newuser',
              email: 'new@example.com',
              password: 'password'
            })}
          >
            Register
          </button>
        </>
      )}
      {error  <div data-testid="error-message">{error}</div>}
      {loading  <div data-testid="loading-indicator">Loading.</div>}
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear mocks before each test
    jest.clearAllMocks()
    // Clear localStorage
    localStorage.clear()
  })
  
  test('provides initial unauthenticated state', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated')
  })
  
  test('login sets authenticated state on success', async () => {
    // Mock successful login response
    axios.post.mockResolvedValueOnce({
      data: { access_token: 'test-token' }
    })
    
    // Mock successful user fetch
    axios.get.mockResolvedValueOnce({
      data: { username: 'testuser', email: 'test@example.com' }
    })
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    // Click login button
    await act(async () => {
      userEvent.click(screen.getByTestId('login-button'))
    })
    
    // Wait for authenticated state
    await waitFor(() => {
      expect(screen.getByTestId('user-info')).toHaveTextContent('testuser')
    })
    
    // Verify axios was called correctly
    expect(axios.post).toHaveBeenCalledWith('/api/token', expect.any(FormData))
    expect(axios.get).toHaveBeenCalledWith('/api/users/me', expect.any(Object))
    
    // Verify token was stored in localStorage
    expect(localStorage.getItem('token')).toBe('test-token')
  })
  
  test('login handles errors correctly', async () => {
    // Mock failed login response
    axios.post.mockRejectedValueOnce({
      response: { data: { detail: 'Invalid credentials' } }
    })
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    // Click login button
    await act(async () => {
      userEvent.click(screen.getByTestId('login-button'))
    })
    
    // Should still be unauthenticated and show error
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated')
      expect(screen.getByTestId('error-message')).toHaveTextContent('Invalid credentials')
    })
  })
  
  test('register works correctly', async () => {
    // Mock successful register response
    axios.post.mockResolvedValueOnce({
      data: { username: 'newuser', email: 'new@example.com' }
    })
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    // Click register button
    await act(async () => {
      userEvent.click(screen.getByTestId('register-button'))
    })
    
    // Should have called register API correctly
    expect(axios.post).toHaveBeenCalledWith('/api/register', {
      username: 'newuser',
      email: 'new@example.com',
      password: 'password'
    })
  })
  
  test('register handles errors correctly', async () => {
    // Mock failed register response
    axios.post.mockRejectedValueOnce({
      response: { data: { detail: 'Username already exists' } }
    })
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    // Click register button
    await act(async () => {
      userEvent.click(screen.getByTestId('register-button'))
    })
    
    // Should show error
    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toHaveTextContent('Username already exists')
    })
  })
  
  test('logout clears authenticated state', async () => {
    // Setup initial authenticated state
    localStorage.setItem('token', 'test-token')
    
    // Mock successful user fetch
    axios.get.mockResolvedValueOnce({
      data: { username: 'testuser', email: 'test@example.com' }
    })
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    // Wait for authenticated state
    await waitFor(() => {
      expect(screen.getByTestId('user-info')).toBeInTheDocument()
    })
    
    // Click logout button
    await act(async () => {
      userEvent.click(screen.getByTestId('logout-button'))
    })
    
    // Should be unauthenticated again
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated')
    })
    
    // Token should be removed from localStorage
    expect(localStorage.getItem('token')).toBeNull()
  })
})
