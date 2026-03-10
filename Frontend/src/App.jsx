import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SignIn from './Pages/SignIn';
import ChatBot from './Pages/ChatBot';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/chatbot" element={<ChatBot />} />
        {/* Redirect unknown routes to SignIn */}
        <Route path="*" element={<SignIn />} />
      </Routes>
    </Router>
  );
}

export default App;
