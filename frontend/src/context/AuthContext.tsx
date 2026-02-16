import React, { createContext, useContext, useState, useEffect } from 'react';
import { getCurrentUser } from '../services/api';
import { auth } from '../config/firebase';
import {
  createUserWithEmailAndPassword,
  GoogleAuthProvider,
  onIdTokenChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
} from 'firebase/auth';

interface AuthContextType {
  user: any | null;
  loading: boolean;
  login: (data: any) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      localStorage.removeItem('token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const unsub = onIdTokenChanged(auth, async (firebaseUser) => {
      if (!firebaseUser) {
        localStorage.removeItem('token');
        setUser(null);
        setLoading(false);
        return;
      }

      const token = await firebaseUser.getIdToken();
      localStorage.setItem('token', token);
      await fetchUser();
    });

    return () => unsub();
  }, []);

  const login = async (data: any) => {
    await signInWithEmailAndPassword(auth, data.email, data.password);
    const token = await auth.currentUser?.getIdToken();
    if (token) localStorage.setItem('token', token);
    await fetchUser();
  };

  const loginWithGoogle = async () => {
    const provider = new GoogleAuthProvider();
    await signInWithPopup(auth, provider);
    const token = await auth.currentUser?.getIdToken();
    if (token) localStorage.setItem('token', token);
    await fetchUser();
  };

  const register = async (data: any) => {
    await createUserWithEmailAndPassword(auth, data.email, data.password);
    const token = await auth.currentUser?.getIdToken();
    if (token) localStorage.setItem('token', token);
    await fetchUser();
  };

  const logout = () => {
    signOut(auth).catch((err) => console.error('Firebase signout failed', err));
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      loginWithGoogle,
      register,
      logout,
      isAuthenticated: !!user
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
