import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LoginForm from '///components/auth/LoginForm'
import { AuthProvider } from '///context/AuthContext'

// Mock the useAuth hook
jest.mock('///context/AuthContext', () => {
  const originalModule = jest.requireActual('///context/AuthContext')
  return {
    .originalModule,
    useAuth: jest.fn(() => ({
      login: jest.fn(),
      error: null,
      loading: false
    }))
  }
})

describe('LoginForm', () => {
  const mockLogin = jest.fn()
  const mockOnSuccess = jest.fn()
  
  beforeEach(() => {
    jest.clearAllMocks()
    // Update mock implementation
    require('///context/AuthContext').useAuth.mockImplementation(() => ({
      login: mockLogin,
      error: null,
      loading: false
    }))
  })
  
  test('renders login form correctly', () => {
    render(<LoginForm onSuccess={mockOnSuccess} />)
    
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })
  
  test('handles form submission correctly', async () => {
    mockLogin.mockResolvedValue(true)
    
    render(<LoginForm onSuccess={mockOnSuccess} />)
    
    // Fill in the form
    userEvent.type(screen.getByLabelText(/username/i), 'testuser')
    userEvent.type(screen.getByLabelText(/password/i), 'password123')
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))
    
    // Verify login was called with correct credentials
    expect(mockLogin).toHaveBeenCalledWith('testuser', 'password123')
    
    // Wait for success callback
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })
  
  test('shows loading state', () => {
    require('///context/AuthContext').useAuth.mockImplementation(() => ({
      login: mockLogin,
      error: null,
      loading: true
    }))
    
    render(<LoginForm onSuccess={mockOnSuccess} />)
    
    expect(screen.getByRole('button', { name: /logging in/i })).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeDisabled()
  })
  
  test('displays error message', () => {
    require('///context/AuthContext').useAuth.mockImplementation(() => ({
      login: mockLogin,
      error: 'Invalid credentials',
      loading: false
    }))
    
    render(<LoginForm onSuccess={mockOnSuccess} />)
    
    expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
  })
  
  test('does not call onSuccess when login fails', async () => {
    mockLogin.mockResolvedValue(false)
    
    render(<LoginForm onSuccess={mockOnSuccess} />)
    
    userEvent.type(screen.getByLabelText(/username/i), 'testuser')
    userEvent.type(screen.getByLabelText(/password/i), 'wrongpass')
    
    fireEvent.click(screen.getByRole('button'))
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalled()
    })
    
    expect(mockOnSuccess).not.toHaveBeenCalled()
  })
})
