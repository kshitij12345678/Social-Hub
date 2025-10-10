/**
 * Phase 5: Enhanced Profile Page
 * Profile page with real backend integration and post upload functionality
 */

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
    id: user.id.toString(),
    name: user.full_name,
    email: user.email,
    avatar: user.full_name.split(' ').map((n: string) => n[0]).join('').toUpperCase(),
    bio: user.bio || 'Welcome to my profile!',
    education_school: '',
    education_degree: '',
    location: user.location || '',
    phone: '',
    profile_picture_url: user.profile_picture_url || '',
    following: 0,
    followers: posts.length, // Use posts count as placeholder
  };

  // Load user posts
  const loadUserPosts = useCallback(async () => {
    if (!isAuthenticated || !user) return;
    
    try {
      setError(null);
      setIsLoading(true);

      // Load current user's posts using the getUserPosts endpoint
      const response = await apiService.getUserPosts(user.id);
      
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
  }, [isAuthenticated, user, toast]);

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
          {/* User Profile Section */}
          <div className="lg:col-span-1">
            <UserProfile user={profileUser} />
            
            {/* Create Post Button */}
            <Card className="mt-6">
              <CardContent className="p-4">
                <Button
                  onClick={() => setShowCreatePost(!showCreatePost)}
                  className="w-full flex items-center space-x-2"
                  size="lg"
                >
                  <Plus className="h-5 w-5" />
                  <span>Create Post</span>
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Posts Section */}
          <div className="lg:col-span-2">
            {/* Create Post Component */}
            {showCreatePost && (
              <div className="mb-6">
                <CreatePost
                  onPostCreated={handlePostCreated}
                  onCancel={() => setShowCreatePost(false)}
                />
              </div>
            )}

            {/* Error State */}
            {error && (
              <Alert className="mb-6">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Card>
              <CardContent className="p-0">
                <Tabs defaultValue="posts" className="w-full">
                  <TabsList className="w-full justify-start rounded-none border-b bg-transparent h-auto p-0">
                    <TabsTrigger 
                      value="posts" 
                      className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-4"
                    >
                      Posts ({posts.length})
                    </TabsTrigger>
                    <TabsTrigger 
                      value="photos" 
                      className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-4"
                    >
                      <Camera className="h-4 w-4 mr-2" />
                      Photos ({photoPosts.length})
                    </TabsTrigger>
                    <TabsTrigger 
                      value="videos" 
                      className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-6 py-4"
                    >
                      <Video className="h-4 w-4 mr-2" />
                      Videos ({videoPosts.length})
                    </TabsTrigger>
                  </TabsList>

                  <div className="p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-2">
                        <Button
                          variant={viewMode === 'grid' ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => setViewMode('grid')}
                        >
                          <Grid className="h-4 w-4" />
                        </Button>
                        <Button
                          variant={viewMode === 'list' ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => setViewMode('list')}
                        >
                          <List className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={loadUserPosts}
                        disabled={isLoading}
                      >
                        {isLoading ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          'Refresh'
                        )}
                      </Button>
                    </div>
                  </div>

                  {/* Loading State */}
                  {isLoading && (
                    <div className="flex justify-center items-center py-12">
                      <Loader2 className="h-8 w-8 animate-spin" />
                      <span className="ml-2">Loading posts...</span>
                    </div>
                  )}

                  {/* Posts Tab */}
                  <TabsContent value="posts" className="p-4">
                    {!isLoading && (
                      <>
                        {viewMode === 'list' ? (
                          <div className="space-y-6">
                            {posts.length > 0 ? (
                              posts.map((post) => (
                                <PostCard 
                                  key={post.id} 
                                  post={post}
                                  onPostUpdate={handlePostUpdate}
                                />
                              ))
                            ) : (
                              <div className="text-center py-12">
                                <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                                  <Grid className="h-8 w-8 text-muted-foreground" />
                                </div>
                                <h3 className="text-lg font-semibold mb-2">No posts yet</h3>
                                <p className="text-muted-foreground mb-4">Share your travel experiences!</p>
                                <Button onClick={() => setShowCreatePost(true)}>
                                  Create Your First Post
                                </Button>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {posts.length > 0 ? (
                              posts.map((post) => (
                                <Card key={post.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                                  <CardContent className="p-0">
                                    {post.media_url ? (
                                      <div className="aspect-square relative">
                                        {post.media_type === 'video' ? (
                                          <video
                                            src={post.media_url}
                                            className="w-full h-full object-cover rounded-t-lg"
                                            poster={post.media_url}
                                          />
                                        ) : (
                                          <img
                                            src={post.media_url}
                                            alt="Post content"
                                            className="w-full h-full object-cover rounded-t-lg"
                                          />
                                        )}
                                        <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-30 transition-opacity flex items-center justify-center">
                                          <div className="text-white opacity-0 hover:opacity-100 transition-opacity text-center">
                                            <p className="text-sm font-semibold">{post.likes_count} ❤️</p>
                                            <p className="text-sm font-semibold">{post.comments_count} 💬</p>
                                          </div>
                                        </div>
                                      </div>
                                    ) : (
                                      <div className="aspect-square bg-muted flex items-center justify-center">
                                        <span className="text-4xl">📝</span>
                                      </div>
                                    )}
                                    <div className="p-3">
                                      <p className="text-sm line-clamp-2">{post.caption}</p>
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
                                <p className="text-muted-foreground mb-4">Share your travel experiences!</p>
                                <Button onClick={() => setShowCreatePost(true)}>
                                  Create Your First Post
                                </Button>
                              </div>
                            )}
                          </div>
                        )}
                      </>
                    )}
                  </TabsContent>

                  {/* Photos Tab */}
                  <TabsContent value="photos" className="p-4">
                    {!isLoading && (
                      <>
                        {photoPosts.length > 0 ? (
                          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                            {photoPosts.map((post) => (
                              <div key={post.id} className="aspect-square relative group cursor-pointer">
                                <img
                                  src={post.media_url}
                                  alt="Photo"
                                  className="w-full h-full object-cover rounded-lg"
                                />
                                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity rounded-lg flex items-center justify-center">
                                  <div className="text-white opacity-0 group-hover:opacity-100 transition-opacity text-center">
                                    <p className="text-sm">{post.likes_count} ❤️</p>
                                    <p className="text-sm">{post.comments_count} 💬</p>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center py-12">
                            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                              <Camera className="h-8 w-8 text-muted-foreground" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2">No photos yet</h3>
                            <p className="text-muted-foreground mb-4">Share your travel photos!</p>
                            <Button onClick={() => setShowCreatePost(true)}>
                              Upload Photo
                            </Button>
                          </div>
                        )}
                      </>
                    )}
                  </TabsContent>

                  {/* Videos Tab */}
                  <TabsContent value="videos" className="p-4">
                    {!isLoading && (
                      <>
                        {videoPosts.length > 0 ? (
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {videoPosts.map((post) => (
                              <div key={post.id} className="aspect-video relative group cursor-pointer">
                                <video
                                  src={post.media_url}
                                  className="w-full h-full object-cover rounded-lg"
                                  poster={post.media_url}
                                />
                                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity rounded-lg flex items-center justify-center">
                                  <div className="text-white opacity-0 group-hover:opacity-100 transition-opacity text-center">
                                    <Video className="h-8 w-8 mx-auto mb-2" />
                                    <p className="text-sm">{post.likes_count} ❤️</p>
                                    <p className="text-sm">{post.comments_count} 💬</p>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center py-12">
                            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                              <Video className="h-8 w-8 text-muted-foreground" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2">No videos yet</h3>
                            <p className="text-muted-foreground mb-4">Share your travel videos!</p>
                            <Button onClick={() => setShowCreatePost(true)}>
                              Upload Video
                            </Button>
                          </div>
                        )}
                      </>
                    )}
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