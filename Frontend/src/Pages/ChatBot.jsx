import React, { useState, useEffect, useRef } from 'react';
import './ChatBot.css';

const ChatBot = () => {
  const [chatHistory, setChatHistory] = useState([
    { text: "שלום! איך אני יכול לעזור לך היום?", isUser: false }
  ]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    console.log('Connecting to WebSocket at ws://127.0.0.1:8000/ws');
    const socket = new WebSocket('ws://127.0.0.1:8000/ws');
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
        // חיבור הצ'אנקים להודעה אחת רציפה
        setChatHistory(prev => {
          const updated = [...prev];
          const lastMessage = updated[updated.length - 1];
          
          if (lastMessage && !lastMessage.isUser && !lastMessage.isNew) {
              // Append to the existing bot message if it's the current stream
              updated[updated.length - 1] = {
                ...lastMessage,
                text: lastMessage.text + messageChunk
              };
              return updated;
          } else {
              // This case handles the first chunk of a new bot response
              // We remove the temporary flag if we used one, or just handle it here
              return [...prev]; // Should have been initialized in handleSend or first chunk
          }
        });
      }
    };

    // User's requested logic simplified for integration:
    socket.onmessage = (event) => {
      const messageChunk = event.data;
      if (messageChunk === "__END__") {
        console.log("סיום תשובה");
        setIsTyping(false);
      } else {
        setChatHistory(prev => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;
          // Check if last message is from user. If so, LLM just started responding.
          if (updated[lastIndex].isUser) {
            return [...prev, { text: messageChunk, isUser: false }];
          } else {
            // Append chunk to the bot's current message
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

  return (
    <div className="chatbot-container" dir="rtl">
      <div className="chatbot-header">
        <h3>SmartCampus Bot {isConnected ? <span className="status-online">●</span> : <span className="status-offline">●</span>}</h3>
      </div>
      <div className="chatbot-messages">
        {chatHistory.map((msg, index) => (
          <div key={index} className={`message ${msg.isUser ? 'user-message' : 'bot-message'}`}>
            {msg.text}
          </div>
        ))}
        {isTyping && <div className="typing-indicator">כותב...</div>}
        {!isConnected && <div className="connection-error">מתחבר לשרת... (127.0.0.1:8000)</div>}
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
