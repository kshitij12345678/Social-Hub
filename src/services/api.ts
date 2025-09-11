const API_BASE_URL = 'http://localhost:8001';

export interface RegisterData {
  full_name: string;
  email: string;
  password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: number;
    full_name: string;
    email: string;
    bio?: string;
    education_school?: string;
    education_degree?: string;
    location?: string;
    phone?: string;
    profile_picture_url?: string;
    created_at: string;
  };
}

export interface ApiError {
  detail: string;
}

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData: ApiError = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Auth endpoints
  async register(userData: RegisterData): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(credentials: LoginData): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async googleAuth(token: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/google', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  }

  async logout(): Promise<{ message: string }> {
    const result = await this.request<{ message: string }>('/auth/logout', {
      method: 'POST',
    });
    
    // Clear token from localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    
    return result;
  }

  async getProfile(): Promise<AuthResponse['user']> {
    return this.request<AuthResponse['user']>('/auth/profile');
  }

  async updateProfile(profileData: { 
    full_name: string; 
    bio?: string;
    education_school?: string;
    education_degree?: string;
    location?: string;
    phone?: string;
  }): Promise<AuthResponse['user']> {
    const updatedUser = await this.request<AuthResponse['user']>('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
    
    // Update stored user data
    this.setUser(updatedUser);
    
    return updatedUser;
  }

  async uploadProfilePicture(file: File): Promise<{ message: string; profile_picture_url: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/auth/upload-profile-picture`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.getToken()}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(errorData.detail || 'Failed to upload profile picture');
    }

    return await response.json();
  }

  // Utility methods for token management
  setToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  setUser(user: AuthResponse['user']): void {
    localStorage.setItem('user', JSON.stringify(user));
  }

  getUser(): AuthResponse['user'] | null {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const apiService = new ApiService();
