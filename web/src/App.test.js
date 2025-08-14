import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'
import axios from 'axios'

// Mock axios
jest.mock('axios')

// Mock child components to simplify testing
jest.mock('./components/ChatMessage', () => {
  return function MockChatMessage({ message }) {
    return (
      <div data-testid="chat-message" data-role={message.role}>
        {message.content}
      </div>
    )
  }
})

jest.mock('./components/ChatInput', () => {
  return function MockChatInput({ onSendMessage, loading }) {
    return (
      <div data-testid="chat-input">
        <input 
          type="text" 
          data-testid="chat-input-field" 
          disabled={loading}
        />
        <button 
          onClick={() => onSendMessage('Test question')} 
          disabled={loading}
          data-testid="send-button"
        >
          Send
        </button>
      </div>
    )
  }
})

describe('App Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks()
  })

  test('renders header and welcome message initially', () => {
    render(<App />)
    
    // Check header content
    expect(screen.getByText('Barbot')).toBeInTheDocument()
    expect(screen.getByText('Your virtual mixologist with 20+ years of experience')).toBeInTheDocument()
    
    // Check welcome content
    expect(screen.getByText('Welcome to Barbot!')).toBeInTheDocument()
    expect(screen.getByText('Ask me about any cocktail recipe or mixology question.')).toBeInTheDocument()
    
    // Check preset question buttons
    expect(screen.getByText("What's in a Mojito?")).toBeInTheDocument()
    expect(screen.getByText('Give me a recipe for an Old Fashioned')).toBeInTheDocument()
  })

  test('adds user message and sends API request when clicking suggestion button', async () => {
    // Mock successful API response
    axios.post.mockResolvedValueOnce({
      data: {
        response: {
          name: 'Mojito',
          ingredients: ['Rum', 'Mint', 'Lime', 'Sugar', 'Soda water'],
          instructions: ['Muddle mint', 'Add ingredients', 'Serve cold'],
          description: 'A refreshing cocktail'
        }
      }
    })

    render(<App />)
    
    // Click on a suggestion button
    fireEvent.click(screen.getByText("What's in a Mojito?"))
    
    // Verify that the user message was added
    await waitFor(() => {
      const messages = screen.getAllByTestId('chat-message')
      expect(messages.length).toBe(1)
      expect(messages[0].getAttribute('data-role')).toBe('user')
      expect(messages[0].textContent).toBe("What's in a Mojito?")
    })
    
    // Verify that the API was called
    expect(axios.post).toHaveBeenCalledWith('/api/chat', {
      messages: [{ role: 'user', content: "What's in a Mojito?" }]
    })
    
    // Verify that the assistant response was added
    await waitFor(() => {
      const messages = screen.getAllByTestId('chat-message')
      expect(messages.length).toBe(2)
      expect(messages[1].getAttribute('data-role')).toBe('assistant')
      expect(JSON.parse(messages[1].textContent).name).toBe('Mojito')
    })
  })

  test('handles API error correctly', async () => {
    // Mock API error
    axios.post.mockRejectedValueOnce(new Error('API Error'))

    render(<App />)
    
    // Submit a message
    const sendButton = screen.getByTestId('send-button')
    fireEvent.click(sendButton)
    
    // Verify error message is displayed
    await waitFor(() => {
      const messages = screen.getAllByTestId('chat-message')
      expect(messages.length).toBe(2)
      expect(messages[1].getAttribute('data-role')).toBe('assistant')
      expect(JSON.parse(messages[1].textContent).response).toContain('Sorry, I encountered an error')
    })
  })

  test('disables input while loading and enables after response', async () => {
    // Mock delayed API response
    axios.post.mockImplementationOnce(() => 
      new Promise(resolve => {
        setTimeout(() => {
          resolve({
            data: {
              response: { response: 'Test response' }
            }
          })
        }, 100)
      })
    )

    render(<App />)
    
    // Submit a message
    const sendButton = screen.getByTestId('send-button')
    fireEvent.click(sendButton)
    
    // Verify input is disabled during loading
    expect(screen.getByTestId('chat-input-field')).toBeDisabled()
    expect(sendButton).toBeDisabled()
    
    // Verify input is enabled after response
    await waitFor(() => {
      expect(screen.getByTestId('chat-input-field')).not.toBeDisabled()
      expect(screen.getByTestId('send-button')).not.toBeDisabled()
    })
  })
})
