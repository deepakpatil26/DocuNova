import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Loader2 } from 'lucide-react';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--docu-bg)] flex flex-col items-center justify-center p-6 text-center">
        <Loader2 className="w-10 h-10 text-[var(--docu-accent)] animate-spin mb-6" />
        <h2 className="text-xl font-bold text-[var(--docu-text-main)]">Initializing Session...</h2>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
