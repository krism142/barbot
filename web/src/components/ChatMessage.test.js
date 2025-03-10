import React from 'react'
import { render, screen } from '@testing-library/react'
import ChatMessage from './ChatMessage'

// Create a named export for SyntaxHighlighter mock
const SyntaxHighlighterMock = ({ children }) => <pre data-testid="syntax-highlighter">{children}</pre>

// Mock SyntaxHighlighter to avoid issues with test rendering
jest.mock('react-syntax-highlighter', () => {
  return {
    __esModule: true,
    default: SyntaxHighlighterMock,
    Light: SyntaxHighlighterMock,
    docco: {}
  }
})

jest.mock('react-syntax-highlighter/dist/esm/styles/hljs', () => ({
  docco: {}
}))

describe('ChatMessage Component', () => {
  test('renders user message correctly', () => {
    const userMessage = {
      role: 'user',
      content: 'What is a Mojito?'
    }
    
    render(<ChatMessage message={userMessage} />)
    
    // Verify user message content is displayed
    expect(screen.getByText('What is a Mojito?')).toBeInTheDocument()
  })
  
  test('renders cocktail recipe response correctly', () => {
    const assistantMessage = {
      role: 'assistant',
      content: JSON.stringify({
        name: 'Mojito',
        ingredients: ['White rum', 'Lime juice', 'Sugar', 'Mint', 'Soda water'],
        instructions: ['Muddle mint with sugar and lime juice', 'Add rum and ice', 'Top with soda water'],
        description: 'A refreshing Cuban highball'
      })
    }
    
    render(<ChatMessage message={assistantMessage} />)
    
    // Verify all parts of the cocktail recipe are displayed
    expect(screen.getByText('Mojito')).toBeInTheDocument()
    expect(screen.getByText('A refreshing Cuban highball')).toBeInTheDocument()
    expect(screen.getByText('Ingredients:')).toBeInTheDocument()
    expect(screen.getByText('White rum')).toBeInTheDocument()
    expect(screen.getByText('Instructions:')).toBeInTheDocument()
    expect(screen.getByText('Muddle mint with sugar and lime juice')).toBeInTheDocument()
  })
  
  test('renders general response correctly', () => {
    const assistantMessage = {
      role: 'assistant',
      content: JSON.stringify({
        response: 'The Manhattan is a classic cocktail made with whiskey, sweet vermouth, and bitters.'
      })
    }
    
    render(<ChatMessage message={assistantMessage} />)
    
    // Verify general response is displayed
    expect(screen.getByText('The Manhattan is a classic cocktail made with whiskey, sweet vermouth, and bitters.')).toBeInTheDocument()
  })
  
  test('handles invalid JSON response', () => {
    const assistantMessage = {
      role: 'assistant',
      content: 'This is not valid JSON'
    }
    
    render(<ChatMessage message={assistantMessage} />)
    
    // Verify the raw content is displayed when not valid JSON
    expect(screen.getByText('This is not valid JSON')).toBeInTheDocument()
  })
  
  test('falls back to JSON display for unrecognized formats', () => {
    const assistantMessage = {
      role: 'assistant',
      content: JSON.stringify({
        unknown_field: 'Some data',
        another_field: 'More data'
      })
    }
    
    render(<ChatMessage message={assistantMessage} />)
    
    // Verify the syntax highlighter is used
    expect(screen.getByTestId('syntax-highlighter')).toBeInTheDocument()
  })
})
