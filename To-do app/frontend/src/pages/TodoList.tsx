import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const TodoList: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-purple-400 via-blue-400 to-purple-600">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <div className="text-center">
          <h1 className="text-2xl font-semibold mb-4">Protected Dashboard</h1>
          <p className="text-lg mb-2">Welcome, {user?.username}!</p>
          <p className="text-sm text-gray-600 mb-4">You are successfully authenticated.</p>
        </div>
        <button onClick={logout} className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded w-full">
          Logout
        </button>
      </div>
    </div>
  );
};

export default TodoList;