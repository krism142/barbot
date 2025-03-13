import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import AuthPage from '///components/auth/AuthPage'

// Mock the child components
jest.mock('///components/auth/LoginForm', () => {
  return function MockLoginForm({ onSuccess }) {
    return (
      <div data-testid="login-form">
        <button 
          data-testid="login-success-button" 
          onClick={onSuccess}
        >
          Simulate Login Success
        </button>
      </div>
    )
  }
})

jest.mock('///components/auth/RegisterForm', () => {
  return function MockRegisterForm({ onSuccess }) {
    return (
      <div data-testid="register-form">
        <button 
          data-testid="register-success-button" 
          onClick={onSuccess}
        >
          Simulate Register Success
        </button>
      </div>
    )
  }
})

describe('AuthPage', () => {
  const mockOnAuthSuccess = jest.fn()
  
  beforeEach(() => {
    jest.clearAllMocks()
  })
  
  test('renders login form by default', () => {
    render(<AuthPage onAuthSuccess={mockOnAuthSuccess} />)
    
    expect(screen.getByTestId('login-form')).toBeInTheDocument()
    expect(screen.queryByTestId('register-form')).not.toBeInTheDocument()
  })
  
  test('switches to register form when register tab is clicked', () => {
    render(<AuthPage onAuthSuccess={mockOnAuthSuccess} />)
    
    // Click the register tab
    fireEvent.click(screen.getByRole('button', { name: /register/i }))
    
    expect(screen.queryByTestId('login-form')).not.toBeInTheDocument()
    expect(screen.getByTestId('register-form')).toBeInTheDocument()
  })
  
  test('switches back to login form when login tab is clicked', () => {
    render(<AuthPage onAuthSuccess={mockOnAuthSuccess} />)
    
    // First switch to register
    fireEvent.click(screen.getByRole('button', { name: /register/i }))
    
    // Then switch back to login
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))
    
    expect(screen.getByTestId('login-form')).toBeInTheDocument()
    expect(screen.queryByTestId('register-form')).not.toBeInTheDocument()
  })
  
  test('calls onAuthSuccess when login is successful', () => {
    render(<AuthPage onAuthSuccess={mockOnAuthSuccess} />)
    
    // Simulate successful login
    fireEvent.click(screen.getByTestId('login-success-button'))
    
    expect(mockOnAuthSuccess).toHaveBeenCalled()
  })
  
  test('switches to login tab after successful registration', () => {
    render(<AuthPage onAuthSuccess={mockOnAuthSuccess} />)
    
    // Switch to register
    fireEvent.click(screen.getByRole('button', { name: /register/i }))
    
    // Simulate successful registration
    fireEvent.click(screen.getByTestId('register-success-button'))
    
    // Should switch back to login
    expect(screen.getByTestId('login-form')).toBeInTheDocument()
    expect(screen.queryByTestId('register-form')).not.toBeInTheDocument()
  })
})
