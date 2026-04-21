import { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Restore from localStorage
    const storedToken = localStorage.getItem('token');
    const storedUserId = localStorage.getItem('user_id');

    console.log('🔍 AuthContext init - checking localStorage');
    console.log('  Token found:', storedToken ? `${storedToken.substring(0, 20)}...` : 'null');
    console.log('  User ID found:', storedUserId);

    if (storedToken && storedUserId) {
      console.log('✓ Restored auth from localStorage');
      setToken(storedToken);
      setUser({ id: storedUserId });
    } else {
      console.log('✗ No token/user_id in localStorage');
    }

    setLoading(false);
  }, []);

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
  };

  return (
    <AuthContext.Provider value={{ user, token, setUser, setToken, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
