import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './ChatBot.css';

const API_URL = import.meta.env.VITE_API_URL || 'localhost:8000';

const ChatBot = () => {
  const [chatHistory, setChatHistory] = useState([
    { text: "שלום! איך אני יכול לעזור לך היום?", isUser: false }
  ]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const socketRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Construct WebSocket URL
    const wsUrl = `ws://${API_URL}/ws`;
    console.log(`Connecting to WebSocket at ${wsUrl}`);
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log('WebSocket Connection Opened Successfully');
      setIsConnected(true);
    };

    socket.onmessage = (event) => {
      const messageChunk = event.data;
      if (messageChunk === "__END__") {
        console.log("סיום תשובה");
        setIsTyping(false);
      } else {
        setChatHistory(prev => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;
          
          if (updated[lastIndex].isUser) {
            return [...prev, { text: messageChunk, isUser: false }];
          } else {
            updated[lastIndex] = {
              ...updated[lastIndex],
              text: updated[lastIndex].text + messageChunk
            };
            return updated;
          }
        });
      }
    };

    socket.onclose = (event) => {
      console.log('WebSocket Connection Closed:', event.code, event.reason);
      setIsConnected(false);
      setIsTyping(false);
    };

    socket.onerror = (error) => {
      console.error('WebSocket Error Occurred:', error);
    };

    return () => {
      console.log('Cleaning up WebSocket connection...');
      socket.close();
    };
  }, []);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;

    if (!isConnected) {
      console.warn('Cannot send message: Not connected');
      return;
    }

    // Add user message to UI
    setChatHistory(prev => [...prev, { text: input, isUser: true }]);
    
    setIsTyping(true);

    // Send message via WebSocket
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      console.log('Sending message to server:', input);
      socketRef.current.send(input);
    } else {
      console.error('WebSocket is not in OPEN state.');
      setIsTyping(false);
    }
    
    // Clear input
    setInput('');
  };

  const handleSignOut = () => {
    // Delete the access_token cookie
    document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    navigate('/');
  };

  const renderMessage = (text) => {
    // Split text by **...** patterns to handle bold text
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <div className="chatbot-container" dir="rtl">
      <div className="chatbot-header">
        <button className="signout-button" onClick={handleSignOut}>התנתק</button>
        <h3>SmartCampus Bot {isConnected ? <span className="status-online">●</span> : <span className="status-offline">●</span>}</h3>
      </div>
      <div className="chatbot-messages">
        {chatHistory.map((msg, index) => (
          <div key={index} className={`message ${msg.isUser ? 'user-message' : 'bot-message'}`}>
            {renderMessage(msg.text)}
          </div>
        ))}
        {isTyping && <div className="typing-indicator">כותב...</div>}
        {!isConnected && <div className="connection-error">מתחבר לשרת... ({API_URL})</div>}
      </div>
      <form className="chatbot-input" onSubmit={handleSend}>
        <input 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          placeholder={isConnected ? "הקלד הודעה..." : "מתחבר..."}
          disabled={!isConnected || isTyping}
        />
        <button type="submit" disabled={!isConnected || !input.trim() || isTyping}>שלח</button>
      </form>
    </div>
  );
};

export default ChatBot;
