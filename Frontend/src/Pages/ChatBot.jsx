import React, { useState } from 'react';
import './ChatBot.css';

const ChatBot = () => {
  const [messages, setMessages] = useState([
    { text: "שלום! איך אני יכול לעזור לך היום?", isUser: false }
  ]);
  const [input, setInput] = useState('');

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const newMessages = [...messages, { text: input, isUser: true }];
    setMessages(newMessages);
    setInput('');

    // Simulate bot response
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        text: "אני בוט חכם של SmartCampus. כרגע אני בשלבי פיתוח!", 
        isUser: false 
      }]);
    }, 1000);
  };

  return (
    <div className="chatbot-container" dir="rtl">
      <div className="chatbot-header">
        <h3>SmartCampus Bot</h3>
      </div>
      <div className="chatbot-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.isUser ? 'user-message' : 'bot-message'}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <form className="chatbot-input" onSubmit={handleSend}>
        <input 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          placeholder="הקלד הודעה..."
        />
        <button type="submit">שלח</button>
      </form>
    </div>
  );
};

export default ChatBot;
