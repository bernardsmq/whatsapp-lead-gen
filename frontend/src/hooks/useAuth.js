import { useState, useContext, useCallback } from 'react';
import { authAPI } from '../lib/api';
import { AuthContext } from '../context/AuthContext';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const useLogin = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { setUser, setToken } = useAuth();

  const login = useCallback(async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authAPI.login(email, password);
      const { access_token, user_id } = response.data;

      localStorage.setItem('token', access_token);
      localStorage.setItem('user_id', user_id);

      setToken(access_token);
      setUser({ id: user_id, email });

      return true;
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, [setUser, setToken]);

  return { login, loading, error };
};

export const useRegister = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const register = useCallback(async (email, password, name, role = 'admin') => {
    setLoading(true);
    setError(null);
    try {
      await authAPI.register(email, password, name, role);
      return true;
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return { register, loading, error };
};
