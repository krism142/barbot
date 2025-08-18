import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RegisterForm from '///components/auth/RegisterForm'

// Mock the useAuth hook
jest.mock('///context/AuthContext', () => {
  const originalModule = jest.requireActual('///context/AuthContext')
  return {
    .originalModule,
    useAuth: jest.fn(() => ({
      register: jest.fn(),
      error: null,
      loading: false
    }))
  }
})

describe('RegisterForm', () => {
  const mockRegister = jest.fn()
  const mockOnSuccess = jest.fn()
  
  beforeEach(() => {
    jest.clearAllMocks()
    // Update mock implementation
    require('///context/AuthContext').useAuth.mockImplementation(() => ({
      register: mockRegister,
      error: null,
      loading: false
    }))
  })
  
  test('renders register form correctly', () => {
    render(<RegisterForm onSuccess={mockOnSuccess} />)
    
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument()
  })
  
  test('handles form submission correctly', async () => {
    mockRegister.mockResolvedValue(true)
    
    render(<RegisterForm onSuccess={mockOnSuccess} />)
    
    // Fill in the form
    userEvent.type(screen.getByLabelText(/username/i), 'newuser')
    userEvent.type(screen.getByLabelText(/email/i), 'new@example.com')
    userEvent.type(screen.getByLabelText(/password/i), 'password123')
    userEvent.type(screen.getByLabelText(/full name/i), 'New User')
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /register/i }))
    
    // Verify register was called with correct data
    expect(mockRegister).toHaveBeenCalledWith({
      username: 'newuser',
      email: 'new@example.com',
      password: 'password123',
      full_name: 'New User'
    })
    
    // Wait for success callback
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })
  
  test('shows loading state', () => {
    require('///context/AuthContext').useAuth.mockImplementation(() => ({
      register: mockRegister,
      error: null,
      loading: true
    }))
    
    render(<RegisterForm onSuccess={mockOnSuccess} />)
    
    expect(screen.getByRole('button', { name: /registering/i })).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeDisabled()
  })
  
  test('displays error message', () => {
    require('///context/AuthContext').useAuth.mockImplementation(() => ({
      register: mockRegister,
      error: 'Username already exists',
      loading: false
    }))
    
    render(<RegisterForm onSuccess={mockOnSuccess} />)
    
    expect(screen.getByText('Username already exists')).toBeInTheDocument()
  })
  
  test('does not call onSuccess when registration fails', async () => {
    mockRegister.mockResolvedValue(false)
    
    render(<RegisterForm onSuccess={mockOnSuccess} />)
    
    userEvent.type(screen.getByLabelText(/username/i), 'existinguser')
    userEvent.type(screen.getByLabelText(/email/i), 'existing@example.com')
    userEvent.type(screen.getByLabelText(/password/i), 'password')
    
    fireEvent.click(screen.getByRole('button'))
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalled()
    })
    
    expect(mockOnSuccess).not.toHaveBeenCalled()
  })
  
  test('handles optional fields correctly', async () => {
    mockRegister.mockResolvedValue(true)
    
    render(<RegisterForm onSuccess={mockOnSuccess} />)
    
    // Fill in only required fields
    userEvent.type(screen.getByLabelText(/username/i), 'newuser')
    userEvent.type(screen.getByLabelText(/email/i), 'new@example.com')
    userEvent.type(screen.getByLabelText(/password/i), 'password123')
    // Don't fill in full name
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /register/i }))
    
    // Verify register was called with correct data and undefined full_name
    expect(mockRegister).toHaveBeenCalledWith({
      username: 'newuser',
      email: 'new@example.com',
      password: 'password123',
      full_name: undefined
    })
  })
})
