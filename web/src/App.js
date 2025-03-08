import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';

// Use a relative URL for API calls, which will be handled by our nginx proxy
const API_URL = '/api/chat';

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to the bottom of the chat whenever messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    // Add user message to the chat
    const userMessage = { role: 'user', content: text };
    setMessages([...messages, userMessage]);
    setLoading(true);

    try {
      // Format the messages for the API
      const formattedMessages = [...messages, userMessage].map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // Send the request to the API
      const response = await axios.post(API_URL, {
        messages: formattedMessages
      });

      // Add assistant response to the chat
      const assistantMessage = { 
        role: 'assistant', 
        content: JSON.stringify(response.data.response, null, 2)
      };
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error('Error communicating with the server:', error);
      // Add error message to the chat
      const errorMessage = { 
        role: 'assistant', 
        content: JSON.stringify({
          "response": "Sorry, I encountered an error. Please try again later."
        }, null, 2)
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-indigo-600 text-white p-4 shadow-md">
        <div className="container mx-auto">
          <h1 className="text-2xl font-bold">Barbot</h1>
          <p className="text-sm">Your virtual mixologist with 20+ years of experience</p>
        </div>
      </header>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="container mx-auto max-w-4xl">
          {messages.length === 0 ? (
            <div className="text-center py-10">
              <h2 className="text-2xl font-semibold text-gray-700">Welcome to Barbot!</h2>
              <p className="mt-2 text-gray-500">
                Ask me about any cocktail recipe or mixology question.
              </p>
              <div className="mt-6 grid grid-cols-1 gap-3 md:grid-cols-2">
                <button
                  onClick={() => handleSendMessage("What's in a Mojito?")}
                  className="px-4 py-2 bg-white shadow-sm rounded-lg text-left hover:bg-gray-50"
                >
                  What's in a Mojito?
                </button>
                <button
                  onClick={() => handleSendMessage("Give me a recipe for an Old Fashioned")}
                  className="px-4 py-2 bg-white shadow-sm rounded-lg text-left hover:bg-gray-50"
                >
                  Give me a recipe for an Old Fashioned
                </button>
                <button
                  onClick={() => handleSendMessage("What's a good cocktail with tequila?")}
                  className="px-4 py-2 bg-white shadow-sm rounded-lg text-left hover:bg-gray-50"
                >
                  What's a good cocktail with tequila?
                </button>
                <button
                  onClick={() => handleSendMessage("Tell me about the history of the Martini")}
                  className="px-4 py-2 bg-white shadow-sm rounded-lg text-left hover:bg-gray-50"
                >
                  Tell me about the history of the Martini
                </button>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 bg-white p-4">
        <div className="container mx-auto max-w-4xl">
          <ChatInput onSendMessage={handleSendMessage} loading={loading} />
        </div>
      </div>
    </div>
  );
}

export default App;