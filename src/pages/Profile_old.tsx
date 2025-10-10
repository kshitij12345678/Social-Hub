import React, { useState, useEffect, useCallback } from 'react';
import { Grid, List, Plus, Loader2, Camera, Video } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import ResponsiveLayout from '@/components/layout/responsive-layout';
import UserProfile from '@/components/ui/user-profile';
import PostCard from '@/components/ui/post-card';
import CreatePost from '@/components/ui/create-post';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { apiService, Post } from '@/services/apiService';

const Profile = () => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();
  
  // State management
  const [posts, setPosts] = useState<Post[]>([]);
  const [photoPosts, setPhotoPosts] = useState<Post[]>([]);
  const [videoPosts, setVideoPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreatePost, setShowCreatePost] = useState(false);

  // If not authenticated, show message or redirect
  if (!isAuthenticated || !user) {
    return (
      <ResponsiveLayout>
        <div className="max-w-4xl mx-auto text-center py-12">
          <h2 className="text-2xl font-bold mb-4">Please log in to view your profile</h2>
          <p className="text-muted-foreground">You need to be authenticated to access this page.</p>
        </div>
      </ResponsiveLayout>
    );
  }

  // Convert API user to match the User interface expected by components
  const profileUser = {
    id: user.$id,
    name: user.name,
    email: user.email,
    avatar: user.name.split(' ').map((n: string) => n[0]).join('').toUpperCase(),
    bio: 'Welcome to my profile!',
    education_school: '',
    education_degree: '',
    location: '',
    phone: '',
    profile_picture_url: '',
    following: 0,
    followers: posts.length, // Use posts count as placeholder
  };

  // Load user posts
  const loadUserPosts = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      setError(null);
      setIsLoading(true);

      // Note: We'll need the user ID from the synced backend user
      // For now, we'll load all posts and filter on frontend
      // In production, you'd want a proper user profile endpoint
      const response = await apiService.getFeed(undefined, 100); // Get more posts to show user's posts
      
      // Since we don't have user ID mapping yet, we'll show all posts for demo
      // In production, filter by actual user ID: response.posts.filter(post => post.user.id === backendUserId)
      setPosts(response.posts);
      
      // Separate posts by media type
      const photos = response.posts.filter(post => post.media_type === 'image');
      const videos = response.posts.filter(post => post.media_type === 'video');
      
      setPhotoPosts(photos);
      setVideoPosts(videos);
      
    } catch (err) {
      console.error('Failed to load user posts:', err);
      setError('Failed to load posts. Please try again.');
      toast({
        title: "Error",
        description: "Failed to load your posts.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, toast]);

  // Initialize profile
  useEffect(() => {
    if (isAuthenticated) {
      loadUserPosts();
    }
  }, [isAuthenticated, loadUserPosts]);

  // Handle post updates
  const handlePostUpdate = useCallback((updatedPost: Partial<Post>) => {
    setPosts(prev => prev.map(post => 
      post.id === updatedPost.id 
        ? { ...post, ...updatedPost }
        : post
    ));
  }, []);

  // Handle new post creation
  const handlePostCreated = useCallback((newPost: Post) => {
    setPosts(prev => [newPost, ...prev]);
    
    // Update media-specific arrays
    if (newPost.media_type === 'image') {
      setPhotoPosts(prev => [newPost, ...prev]);
    } else if (newPost.media_type === 'video') {
      setVideoPosts(prev => [newPost, ...prev]);
    }
    
    setShowCreatePost(false);
    toast({
      title: "Post created!",
      description: "Your post has been added to your profile.",
    });
  }, [toast]);

  return (
    <ResponsiveLayout>
      <div className="max-w-4xl mx-auto">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Profile Info */}
          <div className="lg:col-span-1">
            <UserProfile user={profileUser} isOwnProfile={true} />
          </div>

          {/* Posts Section */}
          <div className="lg:col-span-2">
            <Card className="shadow-card animate-fade-in">
              <CardContent className="p-0">
                <Tabs defaultValue="posts" className="w-full">
                  <div className="border-b p-4">
                    <div className="flex items-center justify-between">
                      <TabsList className="grid w-full grid-cols-3 max-w-md">
                        <TabsTrigger value="posts">Posts</TabsTrigger>
                        <TabsTrigger value="photos">Photos</TabsTrigger>
                        <TabsTrigger value="videos">Videos</TabsTrigger>
                      </TabsList>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          variant={viewMode === 'grid' ? 'default' : 'ghost'}
                          size="sm"
                          onClick={() => setViewMode('grid')}
                          className="hover:bg-primary/10"
                        >
                          <Grid className="h-4 w-4" />
                        </Button>
                        <Button
                          variant={viewMode === 'list' ? 'default' : 'ghost'}
                          size="sm"
                          onClick={() => setViewMode('list')}
                          className="hover:bg-primary/10"
                        >
                          <List className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  <TabsContent value="posts" className="p-4">
                    {viewMode === 'list' ? (
                      <div className="space-y-6">
                        {userPosts.length > 0 ? (
                          userPosts.map((post) => (
                            <FeedPostCard key={post.id} post={post} />
                          ))
                        ) : (
                          <div className="text-center py-12">
                            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                              <Grid className="h-8 w-8 text-muted-foreground" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2">No posts yet</h3>
                            <p className="text-muted-foreground">Share your first post to get started!</p>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {userPosts.length > 0 ? (
                          userPosts.map((post) => (
                            <Card key={post.id} className="hover:shadow-soft transition-smooth animate-scale-in">
                              <CardContent className="p-4">
                                <div className="aspect-square bg-muted rounded-lg mb-3 flex items-center justify-center">
                                  <span className="text-4xl">📝</span>
                                </div>
                                <p className="text-sm text-foreground line-clamp-2 mb-2">
                                  {post.content}
                                </p>
                                <div className="flex items-center justify-between text-xs text-muted-foreground">
                                  <span>{post.timestamp}</span>
                                  <span>{post.likes} likes</span>
                                </div>
                              </CardContent>
                            </Card>
                          ))
                        ) : (
                          <div className="col-span-full text-center py-12">
                            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                              <Grid className="h-8 w-8 text-muted-foreground" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2">No posts yet</h3>
                            <p className="text-muted-foreground">Share your first post to get started!</p>
                          </div>
                        )}
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="photos" className="p-4">
                    <div className="text-center py-12">
                      <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">📸</span>
                      </div>
                      <h3 className="text-lg font-semibold mb-2">No photos yet</h3>
                      <p className="text-muted-foreground">Photos you share will appear here</p>
                    </div>
                  </TabsContent>

                  <TabsContent value="videos" className="p-4">
                    <div className="text-center py-12">
                      <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">🎥</span>
                      </div>
                      <h3 className="text-lg font-semibold mb-2">No videos yet</h3>
                      <p className="text-muted-foreground">Videos you share will appear here</p>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </ResponsiveLayout>
  );
};

export default Profile;