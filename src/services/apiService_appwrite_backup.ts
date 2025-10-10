/**
 * Phase 5: Frontend Integration - API Service
 * Connects React frontend to Phase 4 backend APIs
 */

import { account } from '@/config/appwrite';

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

class ApiService {
  private async getAuthHeaders(): Promise<HeadersInit> {
    try {
      const session = await account.getSession('current');
      return {
        'Authorization': `Bearer ${session.secret}`,
        'Content-Type': 'application/json',
      };
    } catch (error) {
      throw new Error('Authentication required');
    }
  }

  private async getAuthHeadersForFormData(): Promise<HeadersInit> {
    try {
      const session = await account.getSession('current');
      return {
        'Authorization': `Bearer ${session.secret}`,
        // Don't set Content-Type for FormData, let browser set it
      };
    } catch (error) {
      throw new Error('Authentication required');
    }
  }

  // Posts API
  async getFeed(cursor?: string, limit: number = 10): Promise<FeedResponse> {
    const headers = await this.getAuthHeaders();
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append('cursor', cursor);

    const response = await fetch(`${API_BASE_URL}/api/posts?${params}`, {
      headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch feed: ${response.statusText}`);
    }

    return response.json();
  }

  async getUserPosts(userId: number, cursor?: string, limit: number = 10): Promise<FeedResponse> {
    const headers = await this.getAuthHeaders();
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append('cursor', cursor);

    const response = await fetch(`${API_BASE_URL}/api/posts/${userId}?${params}`, {
      headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch user posts: ${response.statusText}`);
    }

    return response.json();
  }

  async createPost(caption: string, media?: File, locationId?: number, travelDate?: string): Promise<Post> {
    const headers = await this.getAuthHeadersForFormData();
    
    const formData = new FormData();
    formData.append('caption', caption);
    
    if (media) {
      formData.append('media', media);
    }
    
    if (locationId) {
      formData.append('location_id', locationId.toString());
    }
    
    if (travelDate) {
      formData.append('travel_date', travelDate);
    }

    const response = await fetch(`${API_BASE_URL}/api/posts`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to create post: ${response.statusText}`);
    }

    return response.json();
  }

  // Social Interactions API
  async toggleLike(postId: number): Promise<{ message: string; likes_count: number; is_liked: boolean }> {
    const headers = await this.getAuthHeaders();

    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/like`, {
      method: 'POST',
      headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to toggle like: ${response.statusText}`);
    }

    return response.json();
  }

  async addComment(postId: number, commentText: string): Promise<Comment> {
    const headers = await this.getAuthHeaders();

    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/comment`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ comment_text: commentText }),
    });

    if (!response.ok) {
      throw new Error(`Failed to add comment: ${response.statusText}`);
    }

    return response.json();
  }

  async sharePost(postId: number): Promise<{ message: string; shares_count: number }> {
    const headers = await this.getAuthHeaders();

    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/share`, {
      method: 'POST',
      headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to share post: ${response.statusText}`);
    }

    return response.json();
  }

  async getPostComments(postId: number, cursor?: string, limit: number = 20): Promise<{
    comments: Comment[];
    next_cursor?: string;
    has_more: boolean;
  }> {
    const headers = await this.getAuthHeaders();
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append('cursor', cursor);

    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/comments?${params}`, {
      headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch comments: ${response.statusText}`);
    }

    return response.json();
  }

  async getPostInteractions(postId: number): Promise<{
    post_id: number;
    likes_count: number;
    comments_count: number;
    shares_count: number;
    user_interactions: {
      is_liked: boolean;
      is_shared: boolean;
    };
  }> {
    const headers = await this.getAuthHeaders();

    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/interactions`, {
      headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch interactions: ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiService = new ApiService();