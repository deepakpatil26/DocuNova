import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogIn, Mail, Lock, Loader2 } from 'lucide-react';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { login, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await login({ email, password });
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      await loginWithGoogle();
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Google login failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--docu-bg)] flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        <div className="text-center mb-10">
          <div className="inline-flex p-4 bg-white dark:bg-[var(--docu-sidebar)] border border-[var(--docu-border)] rounded-2xl shadow-sm mb-6">
            <LogIn className="w-8 h-8 text-[var(--docu-accent)]" />
          </div>
          <h1 className="text-3xl font-bold text-[var(--docu-text-main)] tracking-tight mb-2">Welcome Back</h1>
          <p className="text-[var(--docu-text-secondary)]">Sign in to continue your research.</p>
        </div>

        <div className="docu-card p-8">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-100 text-red-600 rounded-xl text-sm font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-xs font-bold text-[var(--docu-text-main)] uppercase tracking-widest mb-2 ml-1">
                Email Address
              </label>
              <div className="relative">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="docu-input docu-input-icon w-full"
                  placeholder="name@example.com"
                />
                <Mail className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-[var(--docu-text-secondary)]" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-[var(--docu-text-main)] uppercase tracking-widest mb-2 ml-1">
                Password
              </label>
              <div className="relative">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="docu-input docu-input-icon w-full"
                  placeholder="••••••••"
                />
                <Lock className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-[var(--docu-text-secondary)]" />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full h-12 bg-[var(--btn-primary-bg)] text-[var(--btn-primary-text)] font-bold rounded-xl hover:opacity-90 transition-opacity flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Sign In'}
            </button>
          </form>

          <div className="mt-8 flex items-center gap-4 text-[var(--docu-text-secondary)] mb-8">
            <div className="flex-1 h-px bg-[var(--docu-border)]" />
            <span className="text-xs font-bold uppercase tracking-widest">or</span>
            <div className="flex-1 h-px bg-[var(--docu-border)]" />
          </div>

          <button
            onClick={handleGoogleLogin}
            className="w-full h-12 bg-[var(--btn-secondary-bg)] border border-[var(--docu-border)] text-[var(--btn-secondary-text)] font-bold rounded-xl hover:bg-[var(--docu-sidebar)] transition-colors flex items-center justify-center gap-3 shadow-sm active:scale-[0.98]"
          >
            <img src="https://www.google.com/favicon.ico" className="w-5 h-5" alt="Google" />
            Continue with Google
          </button>
        </div>

        <p className="mt-10 text-center text-[var(--docu-text-secondary)] text-sm">
          Don't have an account?{' '}
          <Link to="/signup" className="text-[var(--docu-text-main)] font-bold hover:underline">
            Sign up for free
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
