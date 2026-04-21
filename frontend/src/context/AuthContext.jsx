import { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Restore from localStorage and verify token is still valid
    const storedToken = localStorage.getItem('token');
    const storedUserId = localStorage.getItem('user_id');

    if (storedToken && storedUserId) {
      // Verify token is still valid by calling /auth/verify
      const verifyToken = async () => {
        try {
          const response = await fetch(
            `${import.meta.env.VITE_API_URL || 'https://whatsapp-lead-gen-production.up.railway.app'}/auth/verify`,
            {
              headers: {
                'Authorization': `Bearer ${storedToken}`
              }
            }
          );

          if (response.ok) {
            console.log('✓ Token verified - setting auth');
            setToken(storedToken);
            setUser({ id: storedUserId });
          } else {
            console.log('✗ Token invalid (', response.status, ') - clearing');
            localStorage.removeItem('token');
            localStorage.removeItem('user_id');
          }
        } catch (err) {
          console.error('✗ Error verifying token:', err);
          localStorage.removeItem('token');
          localStorage.removeItem('user_id');
        } finally {
          setLoading(false);
        }
      };

      verifyToken();
    } else {
      setLoading(false);
    }
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
