import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../api';

const useTokenExpiration = () => {
  const { token, logout, login } = useAuth();
  const [showWarning, setShowWarning] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);

  const checkTokenExpiration = useCallback(() => {
    if (!token) return;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      if (payload && payload.exp) {
        const expirationTime = payload.exp * 1000;
        const currentTime = Date.now();
        const timeLeft = expirationTime - currentTime;

        // Show warning 1 minute before expiration
        if (timeLeft > 0 && timeLeft < 60000) {
          setShowWarning(true);
          setTimeRemaining(Math.floor(timeLeft / 1000));
        } else if (timeLeft <= 0) {
          logout();
        } else {
          setShowWarning(false);
        }
      }
    } catch (error) {
      console.error('Error checking token expiration:', error);
    }
  }, [token, logout]);

  const extendSession = async () => {
    try {
      setShowWarning(false);
      
      
    } catch (error) {
      console.error('Error extending session:', error);
      logout();
    }
  };

  useEffect(() => {
    if (token) {
      
      checkTokenExpiration();
      const intervalId = setInterval(checkTokenExpiration, 10000);
      return () => clearInterval(intervalId);
    }
  }, [token, checkTokenExpiration]);

  return {
    showWarning,
    timeRemaining,
    extendSession,
    logout
  };
};

export default useTokenExpiration;