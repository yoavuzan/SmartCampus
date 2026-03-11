import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import SignIn from './Pages/SignIn';
import ChatBot from './Pages/ChatBot';
import './App.css';

// Function to check if the user is authenticated (has access_token cookie)
const isAuthenticated = () => {
  return document.cookie.split('; ').some(row => row.startsWith('access_token='));
};

// ProtectedRoute component to prevent access to /chatbot without a token
const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/" replace />;
  }
  return children;
};

// PublicRoute component to redirect already logged-in users away from / to /chatbot
const PublicRoute = ({ children }) => {
  if (isAuthenticated()) {
    return <Navigate to="/chatbot" replace />;
  }
  return children;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={
            <PublicRoute>
              <SignIn />
            </PublicRoute>
          } 
        />
        <Route 
          path="/chatbot" 
          element={
            <ProtectedRoute>
              <ChatBot />
            </ProtectedRoute>
          } 
        />
        {/* Redirect unknown routes to the landing page */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
