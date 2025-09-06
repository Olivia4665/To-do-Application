import React from 'react';
import useTokenExpiration from '../hooks/useTokenExpiration';
import TokenExpirationModal from './TokenExpirationModal';

const TokenExpirationHandler: React.FC = () => {
  const { showWarning, timeRemaining, extendSession, logout } = useTokenExpiration();

  return (
    <TokenExpirationModal
      show={showWarning}
      onExtend={extendSession}
      onLogout={logout}
      timeRemaining={timeRemaining}
    />
  );
};

export default TokenExpirationHandler;