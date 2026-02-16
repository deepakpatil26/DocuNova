// Import the functions you need from the SDKs you need
import { initializeApp } from 'firebase/app';
import { getAnalytics } from 'firebase/analytics';
import { getAuth } from 'firebase/auth';

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: 'AIzaSyCZpSnXk1UdySrhJtlKqua7TSY8ETWmejE',
  authDomain: 'docuchat-9fe8c.firebaseapp.com',
  projectId: 'docuchat-9fe8c',
  storageBucket: 'docuchat-9fe8c.firebasestorage.app',
  messagingSenderId: '853487653700',
  appId: '1:853487653700:web:f76f7055f23dabae82bd11',
  measurementId: 'G-RZ7FC8D1XN',
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);

export { app, analytics, auth };
