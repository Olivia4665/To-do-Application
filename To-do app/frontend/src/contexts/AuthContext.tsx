import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

declare global {
  interface Window {
    axios: typeof axios;
  }
}

interface User {
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = () => {
      try {
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');
        
        if (storedToken && storedUser) {
          const parsedUser = JSON.parse(storedUser);
          setToken(storedToken);
          setUser(parsedUser);
          
          
          if (window.axios) {
            window.axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
          }
          
          console.log('Auth restored from localStorage:', { token: storedToken, user: parsedUser });
        }
      } catch (error) {
        console.error('Error restoring auth from localStorage:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = (newToken: string, newUser: User) => {
    try {
      console.log('AuthContext: Logging in user:', newUser);
      
      // Update state
      setToken(newToken);
      setUser(newUser);
      localStorage.setItem('token', newToken);
      localStorage.setItem('user', JSON.stringify(newUser));
      
      if (window.axios) {
        window.axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      }
      
      console.log('AuthContext: Login successful, token and user saved');
    } catch (error) {
      console.error('Error during login:', error);
    }
  };

  const logout = () => {
    console.log('AuthContext: Logging out user');
    
    
    setToken(null);
    setUser(null);
    
  
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    if (window.axios) {
      delete window.axios.defaults.headers.common['Authorization'];
    }
    
    window.location.href = '/login';
  };

  const isAuthenticated = !!(token && user);

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};