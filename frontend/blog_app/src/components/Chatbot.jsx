import React, { useState, useRef, useEffect } from 'react';

const ChatbotComponent = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    // Add user message
    const userMessage = { sender: 'user', text: input };
    setMessages([...messages, userMessage]);
    setInput(''); // Clear input immediately after submit
    setLoading(true);
    
    try {
      // Call backend API
      const response = await fetch('http://localhost:8005/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: input }),
      });
      
      const data = await response.json();
      
      // Add bot message
      const botMessage = { 
        sender: 'bot', 
        text: data.answer, 
        hasAnswer: data.has_answer 
      };
      
      setMessages(prevMessages => [...prevMessages, botMessage]);
    } catch (error) {
      console.error('Error fetching response:', error);
      const errorMessage = { 
        sender: 'bot', 
        text: 'Sorry, I encountered an error while processing your request.', 
        hasAnswer: false 
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    }
    
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-[650px] w-[1000px] max-w-8xl -ml-13 mx-auto bg-gray-300 rounded-xl overflow-hidden shadow-2xl border border-gray-600">
      {/* Chat messages */}
      <div className="flex-1 p-1 overflow-y-auto bg-gray-200">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-16 h-16 bg-gray-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-gray-500 text-lg font-medium mb-2">Welcome to BloQ!</h3>
              <p className="text-gray-500">Ask me something about our blog posts and I'll help you find the information you need.</p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((message, index) => (
              <div 
                key={index} 
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div 
                  className={`max-w-[80%] p-4 rounded-xl shadow-lg ${
                    message.sender === 'user' 
                      ? 'bg-gray-400 m-3 text-white rounded-br-none' 
                      : message.hasAnswer 
                        ? 'bg-gray-400 border-slate-500 m-3 rounded-bl-none text-gray-100' 
                        : 'bg-red-900 border border-red-700 rounded-bl-none text-red-100'
                  }`}
                >
                  <div className="whitespace-pre-wrap leading-relaxed">
                    {message.text}
                  </div>
                </div>
              </div>
            ))}
            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-600 border border-slate-500 p-4 rounded-xl rounded-bl-none max-w-[80%] shadow-lg">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0s' }}></div>
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Chat input */}
      <form onSubmit={handleSubmit} className="bg-gray-600 border-t border-gray-600 p-4">
        <div className="flex space-x-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about our blog posts..."
            className="flex-1 px-4 py-3 bg-gray-400 border border-gray-200 rounded-lg text-white placeholder-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-50 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-gray-400 text-white px-6 py-3 rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:ring-offset-gray-700 disabled:bg-gray-500 disabled:opacity-50 transition-colors duration-200 font-medium"
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatbotComponent;
