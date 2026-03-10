import SignIn from './Pages/SignIn'
import './App.css'

function App() {
  return (
<<<<<<< Updated upstream
    <SignIn />
  )
=======
    <Router>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/chatbot" element={<ChatBot />} />
        <Route path="*" element={<SignIn />} />
      </Routes>
    </Router>
  );
>>>>>>> Stashed changes
}

export default App
