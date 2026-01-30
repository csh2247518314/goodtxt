import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI, apiUtils } from '../services/api';

interface User {
  user_id: string;
  username: string;
  email: string;
  role: string;
  api_key: string;
  settings: any;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  register: (username: string, email: string, password: string) => Promise<boolean>;
  loading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // 初始化时检查本地存储的认证信息
    const savedToken = apiUtils.getAuthToken();
    const savedUser = apiUtils.getCurrentUser();

    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(savedUser);
      
      // 验证token有效性
      validateToken(savedToken);
    }
    
    setLoading(false);
  }, []);

  const validateToken = async (tokenToValidate: string) => {
    try {
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
    } catch (error) {
      // Token无效，清除本地存储
      apiUtils.clearAuthToken();
      setToken(null);
      setUser(null);
    }
  };

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);

      const { token: newToken, user: userData } = await authAPI.login(username, password);
      
      setToken(newToken);
      setUser(userData);
      setError(null);
      
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || '登录失败';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);

      await authAPI.register(username, email, password);
      
      // 注册成功后自动登录
      const success = await login(username, password);
      return success;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || '注册失败';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    authAPI.logout();
    setToken(null);
    setUser(null);
    setError(null);
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    register,
    loading,
    error
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};