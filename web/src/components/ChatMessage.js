import React from 'react';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

function ChatMessage({ message }) {
  const { role, content } = message;
  const isUser = role === 'user';

  const formatResponse = (content) => {
    try {
      // Try to parse the content as JSON
      const parsedContent = JSON.parse(content);
      
      // If it's a cocktail recipe
      if (parsedContent.name && parsedContent.ingredients) {
        return (
          <div className="border border-gray-200 rounded-lg p-4 bg-white">
            <h3 className="text-xl font-bold mb-2">{parsedContent.name}</h3>
            <p className="text-gray-600 mb-4">{parsedContent.description}</p>
            
            <h4 className="font-semibold mb-2">Ingredients:</h4>
            <ul className="list-disc pl-5 mb-4">
              {parsedContent.ingredients.map((ingredient, idx) => (
                <li key={idx} className="mb-1">{ingredient}</li>
              ))}
            </ul>
            
            <h4 className="font-semibold mb-2">Instructions:</h4>
            <ol className="list-decimal pl-5">
              {parsedContent.instructions.map((step, idx) => (
                <li key={idx} className="mb-1">{step}</li>
              ))}
            </ol>
          </div>
        );
      }
      
      // If it's just a response
      if (parsedContent.response) {
        return <p>{parsedContent.response}</p>;
      }
      
      // Fallback to JSON display
      return (
        <SyntaxHighlighter language="json" style={docco}>
          {content}
        </SyntaxHighlighter>
      );
    } catch (e) {
      // If it's not valid JSON, just display as text
      return <p>{content}</p>;
    }
  };

  return (
    <div className={`flex mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-3xl rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-indigo-600 text-white rounded-br-none'
            : 'bg-white border border-gray-200 rounded-bl-none'
        }`}
        style={{ width: 'fit-content', maxWidth: '80%' }}
      >
        {isUser ? <p>{content}</p> : formatResponse(content)}
      </div>
    </div>
  );
}

export default ChatMessage;