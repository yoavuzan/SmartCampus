import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './SignIn.css';

const SignIn = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const formData = new URLSearchParams();
      formData.append('username', email); // FastAPI OAuth2 uses 'username' field
      formData.append('password', password);

      const response = await fetch('http://127.0.0.1:8000/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('אימייל או סיסמה שגויים');
      }

      const data = await response.json();
      
      // Save token in cookies (expires in 24 hours)
      const expirationDate = new Date();
      expirationDate.setTime(expirationDate.getTime() + (24 * 60 * 60 * 1000));
      document.cookie = `access_token=${data.access_token}; expires=${expirationDate.toUTCString()}; path=/; SameSite=Strict`;

      console.log('Login successful');
      // Redirect to ChatBot page
      navigate('/chatbot');
      
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="signin-container" dir="rtl">
      <div className="signin-card">
        
        {/* Header */}
        <div className="signin-header">
          <h2 className="signin-title">
            התחברות לחשבון
          </h2>
          <p className="signin-subtitle">
            ברוכים הבאים! אנא הזינו את פרטי ההתחברות שלכם.
          </p>
        </div>

        {error && <div className="error-message" style={{color: 'red', textAlign: 'center', marginBottom: '10px'}}>{error}</div>}

        {/* Google Sign In */}
        <div className="mt-8">
          <button type="button" className="google-button">
            <svg className="h-5 w-5 ml-2" viewBox="0 0 48 48">
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24s.92 7.54 2.56 10.78l7.97-6.19z" />
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
            </svg>
            התחבר באמצעות Google
          </button>
        </div>

        <div className="divider-container">
          <div className="divider-line-wrapper">
            <div className="divider-line"></div>
          </div>
          <div className="divider-text-wrapper">
            <span className="divider-text">או התחבר עם אימייל</span>
          </div>
        </div>

        {/* Login Form */}
        <form className="signin-form" onSubmit={handleSubmit}>
          <div className="input-group">
            <div>
              <label htmlFor="email-address" className="input-label">
                כתובת אימייל
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="input-field"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="input-label">
                סיסמה
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="input-field"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="form-options">
            <div className="checkbox-group">
              <input id="remember-me" name="remember-me" type="checkbox" className="checkbox-input" />
              <label htmlFor="remember-me" className="checkbox-label">
                זכור אותי
              </label>
            </div>

            <div className="text-sm">
              <a href="#" className="forgot-password-link">
                שכחת סיסמה?
              </a>
            </div>
          </div>

          <div>
            <button type="submit" className="submit-button">
              התחבר למערכת
            </button>
          </div>
        </form>

        <div className="signin-footer">
          <p className="footer-text">
            אין לך חשבון עדיין?{' '}
            <a href="#" className="signup-link">
              צור חשבון חדש
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignIn;
