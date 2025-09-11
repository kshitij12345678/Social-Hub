import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService, AuthResponse } from '@/services/api';

interface AuthContextType {
  user: AuthResponse['user'] | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string) => Promise<void>;
  updateProfile: (profileData: {
    full_name: string;
    bio?: string;
    education_school?: string;
    education_degree?: string;
    location?: string;
    phone?: string;
  }) => Promise<void>;
  uploadProfilePicture: (file: File) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<AuthResponse['user'] | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in on app start
    const token = apiService.getToken();
    const savedUser = apiService.getUser();
    
    if (token && savedUser) {
      setUser(savedUser);
    }
    
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    const response = await apiService.login({ email, password });
    apiService.setToken(response.access_token);
    apiService.setUser(response.user);
    setUser(response.user);
  };

  const register = async (fullName: string, email: string, password: string): Promise<void> => {
    const response = await apiService.register({
      full_name: fullName,
      email,
      password,
    });
    apiService.setToken(response.access_token);
    apiService.setUser(response.user);
    setUser(response.user);
  };

  const logout = async (): Promise<void> => {
    await apiService.logout();
    setUser(null);
  };

  const updateProfile = async (profileData: {
    full_name: string;
    bio?: string;
    education_school?: string;
    education_degree?: string;
    location?: string;
    phone?: string;
  }): Promise<void> => {
    const updatedUser = await apiService.updateProfile(profileData);
    setUser(updatedUser);
  };

  const uploadProfilePicture = async (file: File): Promise<void> => {
    const response = await apiService.uploadProfilePicture(file);
    // Update the user state with the new profile picture URL
    if (user) {
      const updatedUser = {
        ...user,
        profile_picture_url: response.profile_picture_url
      };
      setUser(updatedUser);
      // Also update localStorage
      apiService.setUser(updatedUser);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    updateProfile,
    uploadProfilePicture,
    logout,
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
