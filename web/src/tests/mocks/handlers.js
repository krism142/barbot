import { rest } from 'msw';

// Mock data for API responses
const mockMojito = {
  name: "Mojito",
  ingredients: ["White rum", "Fresh lime juice", "Sugar", "Mint leaves", "Soda water"],
  instructions: [
    "Muddle mint leaves with sugar and lime juice",
    "Add rum and fill glass with ice",
    "Top with soda water and garnish with mint sprig"
  ],
  description: "A refreshing Cuban highball"
};

const mockManhattan = {
  response: "The Manhattan is a classic cocktail made with whiskey, sweet vermouth, and bitters."
};

// Define API handlers
export const handlers = [
  // Mock the chat endpoint
  rest.post('/api/chat', (req, res, ctx) => {
    const { messages } = req.body;
    
    // Check the message content to determine the response
    if (messages && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      
      if (lastMessage.content.toLowerCase().includes('mojito')) {
        return res(ctx.status(200), ctx.json({ response: mockMojito }));
      } else if (lastMessage.content.toLowerCase().includes('manhattan')) {
        return res(ctx.status(200), ctx.json({ response: mockManhattan }));
      }
    }
    
    // Default response
    return res(
      ctx.status(200),
      ctx.json({
        response: {
          response: "I'm not sure about that. Could you ask about a specific cocktail?"
        }
      })
    );
  }),
  
  // Mock error response for testing
  rest.post('/api/error', (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({ detail: "Internal server error" }));
  })
];