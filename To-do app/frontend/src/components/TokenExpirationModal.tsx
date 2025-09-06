import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface TokenExpirationModalProps {
  show: boolean;
  onExtend: () => void;
  onLogout: () => void;
  timeRemaining: number;
}

const TokenExpirationModal: React.FC<TokenExpirationModalProps> = ({
  show,
  onExtend,
  onLogout,
  timeRemaining
}) => {
  const [countdown, setCountdown] = useState(timeRemaining);

  useEffect(() => {
    if (show && countdown > 0) {
      const timer = setInterval(() => {
        setCountdown(prev => prev - 1);
      }, 1000);
      return () => clearInterval(timer);
    } else if (countdown === 0) {
      onLogout();
    }
  }, [show, countdown, onLogout]);

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h2 className="text-xl font-bold mb-4">Session About to Expire</h2>
        <p className="mb-4">
          Your session will expire in {countdown} seconds. Would you like to extend it?
        </p>
        <div className="flex justify-end space-x-4">
          <button
            onClick={onLogout}
            className="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
          >
            Logout
          </button>
          <button
            onClick={onExtend}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
          >
            Stay Logged In
          </button>
        </div>
      </div>
    </div>
  );
};

export default TokenExpirationModal;