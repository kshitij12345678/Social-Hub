/**
 * Phase 5: Frontend Integration - JWT API Service
 * Connects React frontend to Phase 4 backend APIs with JWT authentication
 */

const API_BASE_URL = 'http://localhost:8001';

export interface User {
  id: number;
  full_name: string;
  email: string;
  profile_picture_url?: string;
  location?: string;
  bio?: string;
}

export interface Post {
  id: number;
  user: User;
  caption: string;
  media_url?: string;
  media_type?: 'image' | 'video';
  location_id?: number;
  travel_date?: string;
  likes_count: number;
  comments_count: number;
  shares_count: number;
  is_liked_by_user: boolean;
  created_at: string;
}

export interface Comment {
  id: number;
  user: User;
  comment_text: string;
  created_at: string;
}

export interface FeedResponse {
  posts: Post[];
  next_cursor?: string;
  has_more: boolean;
}

export interface CreatePostData {
  caption: string;
  media_url?: string;
  media_type?: 'image' | 'video';
  location_id?: number;
  travel_date?: string;
}

class ApiService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('authToken');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  // Social Media API endpoints

  /**
   * Get personalized feed with infinite scroll
   */
  async getFeed(cursor?: string, limit: number = 10): Promise<FeedResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      ...(cursor && { cursor })
    });

    const response = await fetch(`${API_BASE_URL}/api/posts?${params}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch feed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Create a new post with optional media
   */
  async createPost(postData: CreatePostData & { mediaFile?: File }): Promise<Post> {
    const formData = new FormData();
    formData.append('caption', postData.caption);
    
    if (postData.location_id) {
      formData.append('location_id', postData.location_id.toString());
    }
    
    if (postData.travel_date) {
      formData.append('travel_date', postData.travel_date);
    }

    // Add media file if provided
    if (postData.mediaFile) {
      formData.append('media', postData.mediaFile);
    }
    
    const token = localStorage.getItem('authToken');
    const response = await fetch(`${API_BASE_URL}/api/posts`, {
      method: 'POST',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` })
        // Don't set Content-Type for FormData - browser will set it with boundary
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Failed to create post: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Like/unlike a post
   */
  async toggleLike(postId: number): Promise<{ is_liked: boolean; likes_count: number }> {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/like`, {
      method: 'POST',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to toggle like: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get comments for a post
   */
  async getComments(postId: number, cursor?: string, limit: number = 20): Promise<{
    comments: Comment[];
    next_cursor?: string;
    has_more: boolean;
  }> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      ...(cursor && { cursor })
    });

    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/comments?${params}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch comments: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Add a comment to a post
   */
  async addComment(postId: number, commentText: string): Promise<Comment> {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/comment`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ comment_text: commentText })
    });

    if (!response.ok) {
      throw new Error(`Failed to add comment: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Share a post
   */
  async sharePost(postId: number): Promise<{ shares_count: number }> {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/share`, {
      method: 'POST',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to share post: ${response.statusText}`);
    }

    return response.json();
  }



  /**
   * Get user's own posts
   */
  async getUserPosts(userId?: number, cursor?: string, limit: number = 10): Promise<FeedResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      ...(cursor && { cursor })
    });

    if (!userId) {
      throw new Error('User ID is required to fetch user posts');
    }

    const response = await fetch(`${API_BASE_URL}/api/posts/${userId}?${params}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch user posts: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get user profile
   */
  async getUserProfile(userId?: number): Promise<User> {
    const endpoint = userId ? `/api/users/${userId}` : '/api/users/me';
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch user profile: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Update user profile
   */
  async updateProfile(profileData: Partial<User>): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/api/users/me`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(profileData)
    });

    if (!response.ok) {
      throw new Error(`Failed to update profile: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get search results
   */
  async searchPosts(query: string, cursor?: string, limit: number = 10): Promise<FeedResponse> {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
      ...(cursor && { cursor })
    });

    const response = await fetch(`${API_BASE_URL}/api/search/posts?${params}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to search posts: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get trending posts
   */
  async getTrendingPosts(cursor?: string, limit: number = 10): Promise<FeedResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      ...(cursor && { cursor })
    });

    const response = await fetch(`${API_BASE_URL}/api/trending?${params}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch trending posts: ${response.statusText}`);
    }

    return response.json();
  }

  // ============ RECOMMENDATION SYSTEM ENDPOINTS ============

  /**
   * Get personalized post recommendations
   */
  async getRecommendedPosts(limit: number = 10): Promise<{
    user_id: number;
    recommendations: any[];
    total_count: number;
    recommendation_info: {
      algorithm: string;
      combines: string[];
      personalized: boolean;
    };
  }> {
    const params = new URLSearchParams({
      limit: limit.toString()
    });

    const response = await fetch(`${API_BASE_URL}/api/recommendations/posts?${params}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch recommendations: ${response.statusText}`);
    }

    return response.json();
  }



  /**
   * Get personalized post recommendations
   */
  async getRecommendations(limit: number = 10): Promise<{ recommendations: Post[] }> {
    const response = await fetch(`${API_BASE_URL}/api/recommendations/posts?limit=${limit}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch recommendations: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get popular posts
   */
  async getPopularPosts(limit: number = 10): Promise<{ posts: Post[] }> {
    const response = await fetch(`${API_BASE_URL}/api/recommendations/popular?limit=${limit}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch popular posts: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get recommendation stats for current user
   */
  async getRecommendationStats(): Promise<{
    user_id: number;
    interaction_stats: any;
    recommendation_readiness: any;
    system_info: any;
  }> {
    const response = await fetch(`${API_BASE_URL}/api/recommendations/stats`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch recommendation stats: ${response.statusText}`);
    }

    return response.json();
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export class for testing
export default ApiService;