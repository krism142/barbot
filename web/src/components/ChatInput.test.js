import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ChatInput from './ChatInput'

describe('ChatInput Component', () => {
  const mockSendMessage = jest.fn()
  
  beforeEach(() => {
    mockSendMessage.mockClear()
  })
  
  test('renders input field and button correctly', () => {
    render(<ChatInput onSendMessage={mockSendMessage} loading={false} />)
    
    // Check if input and button are rendered
    const inputField = screen.getByPlaceholderText('Ask about a cocktail or mixology...')
    const sendButton = screen.getByRole('button')
    
    expect(inputField).toBeInTheDocument()
    expect(sendButton).toBeInTheDocument()
    expect(sendButton).not.toBeDisabled()
  })
  
  test('disables input and button when loading', () => {
    render(<ChatInput onSendMessage={mockSendMessage} loading={true} />)
    
    // Check if input and button are disabled when loading
    const inputField = screen.getByPlaceholderText('Barbot is thinking...')
    const sendButton = screen.getByRole('button')
    
    expect(inputField).toBeDisabled()
    expect(sendButton).toBeDisabled()
  })
  
  test('calls onSendMessage when form is submitted', async () => {
    render(<ChatInput onSendMessage={mockSendMessage} loading={false} />)
    
    // Type in the input and submit
    const inputField = screen.getByPlaceholderText('Ask about a cocktail or mixology...')
    await userEvent.type(inputField, 'What is a Mojito?')
    
    // Submit form
    const sendButton = screen.getByRole('button')
    fireEvent.click(sendButton)
    
    // Verify onSendMessage was called with the input text
    expect(mockSendMessage).toHaveBeenCalledWith('What is a Mojito?')
    
    // Verify the input was cleared
    expect(inputField.value).toBe('')
  })
  
  test('prevents submission with empty input', async () => {
    render(<ChatInput onSendMessage={mockSendMessage} loading={false} />)
    
    // Try to submit without any input
    const sendButton = screen.getByRole('button')
    fireEvent.click(sendButton)
    
    // Verify onSendMessage was not called
    expect(mockSendMessage).not.toHaveBeenCalled()
  })
  
  test('handles keyboard submission with Enter key', async () => {
    render(<ChatInput onSendMessage={mockSendMessage} loading={false} />)
    
    // Type in the input
    const inputField = screen.getByPlaceholderText('Ask about a cocktail or mixology...')
    await userEvent.type(inputField, 'What is a Mojito?{enter}')
    
    // Verify onSendMessage was called with the input text
    expect(mockSendMessage).toHaveBeenCalledWith('What is a Mojito?')
  })
  
  test('does not submit when loading even if input has text', async () => {
    // First render without loading to type text
    const { rerender } = render(<ChatInput onSendMessage={mockSendMessage} loading={false} />)
    
    // Type in the input
    const inputField = screen.getByPlaceholderText('Ask about a cocktail or mixology...')
    await userEvent.type(inputField, 'What is a Mojito?')
    
    // Rerender with loading=true
    rerender(<ChatInput onSendMessage={mockSendMessage} loading={true} />)
    
    // Try to submit form
    const sendButton = screen.getByRole('button')
    fireEvent.click(sendButton)
    
    // Verify onSendMessage was not called
    expect(mockSendMessage).not.toHaveBeenCalled()
  })
})
