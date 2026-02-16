import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Loader2 } from 'lucide-react';

const OAuthCallback: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get('token');

    if (token) {
      localStorage.setItem('token', token);
      // We might need to refresh the page or trigger a re-fetch in AuthContext
      window.location.href = '/';
    } else {
      navigate('/login', { state: { error: 'Google Login failed. No token received.' } });
    }
  }, [location, navigate]);

  return (
    <div className="min-h-screen bg-[var(--docu-bg)] flex flex-col items-center justify-center p-6 text-center">
      <Loader2 className="w-10 h-10 text-[var(--docu-accent)] animate-spin mb-6" />
      <h2 className="text-xl font-bold text-[var(--docu-text-main)]">Completing Login...</h2>
      <p className="text-[var(--docu-text-secondary)] mt-2">Setting up your secure workspace.</p>
    </div>
  );
};

export default OAuthCallback;
