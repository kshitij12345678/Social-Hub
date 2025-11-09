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
   * Update a post (only caption)
   */
  async updatePost(postId: number, updateData: { caption?: string }): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(updateData)
    });

    if (!response.ok) {
      throw new Error(`Failed to update post: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Delete a post
   */
  async deletePost(postId: number): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to delete post: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Search posts
   */
  async searchPosts(query: string, limit: number = 20): Promise<{
    query: string;
    results: Post[];
    count: number;
  }> {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString()
    });

    const response = await fetch(`${API_BASE_URL}/search?${params}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to search posts: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Transform backend response to match frontend Post interface
    const transformedResults: Post[] = data.results.map((post: any) => ({
      id: post.id,
      user: {
        id: post.user_id,
        full_name: post.author_name,
        profile_picture_url: post.author_profile_picture,
        email: '', // Not provided in search response
        bio: '',
        education_school: null,
        education_degree: null,
        location: null,
        phone: null,
      },
      caption: post.caption,
      media_url: post.media_url,
      media_type: post.media_type,
      location_id: post.location_id,
      travel_date: post.travel_date,
      likes_count: post.likes_count,
      comments_count: post.comments_count,
      shares_count: post.shares_count,
      is_liked_by_user: post.is_liked,
      created_at: post.created_at,
    }));

    return {
      query: data.query,
      results: transformedResults,
      count: data.count
    };
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