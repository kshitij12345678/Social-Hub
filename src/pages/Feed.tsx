import React, { useState, useEffect, useCallback } from 'react';
import { PlusCircle, RefreshCw, Loader2, Sparkles, Brain } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import ResponsiveLayout from '@/components/layout/responsive-layout';
import PostCard from '@/components/ui/post-card';
import CreatePost from '@/components/ui/create-post';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { apiService, Post } from '@/services/apiService';

const Feed = () => {
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();
  
  // State management - Only AI recommended posts
  const [recommendedPosts, setRecommendedPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [algorithmStats, setAlgorithmStats] = useState<{[key: string]: number}>({});

  // Load AI recommended posts
  const loadRecommendedPosts = useCallback(async (refresh = false) => {
    if (!isAuthenticated) return;
    
    try {
      setError(null);
      if (refresh) {
        setIsLoading(true);
        setRecommendedPosts([]);
      }

      const response = await apiService.getRecommendations(20); // Get more recommendations
      
      setRecommendedPosts(response.recommendations);
      
      // Calculate algorithm distribution
      const stats: {[key: string]: number} = {};
      response.recommendations.forEach((post: any) => {
        const algorithm = post.algorithm || 'unknown';
        stats[algorithm] = (stats[algorithm] || 0) + 1;
      });
      setAlgorithmStats(stats);
      
    } catch (err) {
      console.error('Failed to load posts:', err);
      setError('Failed to load posts. Please try again.');
      toast({
        title: "Error",
        description: "Failed to load posts. Please check your connection.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, toast]);



  // Initialize AI feed
  useEffect(() => {
    if (isAuthenticated) {
      loadRecommendedPosts();
    }
  }, [isAuthenticated, loadRecommendedPosts]);

  // Handle post updates (likes, shares, etc.)
  const handlePostUpdate = useCallback((updatedPost: Partial<Post>) => {
    setRecommendedPosts(prev => prev.map(post => 
      post.id === updatedPost.id 
        ? { ...post, ...updatedPost }
        : post
    ));
  }, []);

  // Handle new post creation
  const handlePostCreated = useCallback((newPost: Post) => {
    setShowCreatePost(false);
    
    // Refresh recommendations to potentially include the new post
    loadRecommendedPosts(true);
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    toast({
      title: "Post created!",
      description: "Your post has been created. Refreshing AI recommendations...",
    });
  }, [loadRecommendedPosts, toast]);

  // Show authentication required message
  if (!isAuthenticated) {
    return (
      <ResponsiveLayout>
        <div className="max-w-2xl mx-auto">
          <Alert>
            <AlertDescription>
              Please log in to view your personalized feed.
            </AlertDescription>
          </Alert>
        </div>
      </ResponsiveLayout>
    );
  }

  return (
    <ResponsiveLayout>
      <div className="max-w-2xl mx-auto">


        {/* Action Buttons */}
        <div className="mb-6 flex justify-center space-x-3">
          <Button
            onClick={() => setShowCreatePost(!showCreatePost)}
            className="flex items-center space-x-2"
          >
            <PlusCircle className="h-4 w-4" />
            <span>Create Post</span>
          </Button>
          
                    <Button
            variant="outline"
            size="sm"
            onClick={() => loadRecommendedPosts(true)}
            disabled={isLoading}
            className="flex items-center space-x-2"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>
        </div>

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

        {/* Loading State */}
        {isLoading && (
          <div className="flex flex-col justify-center items-center py-12">
            <Loader2 className="h-8 w-8 animate-spin mb-4" />
            <p className="text-lg font-medium">AI is curating your feed...</p>
            <p className="text-muted-foreground text-sm">Finding the best content for you</p>
          </div>
        )}

        {/* AI Recommended Posts Feed */}
        {!isLoading && (
          <>
            {recommendedPosts.length === 0 ? (
              <Card>
                <CardContent className="pt-6 text-center py-12">
                  <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">Building your AI profile</h3>
                  <p className="text-muted-foreground mb-4">
                    Interact with some posts to help our AI learn your preferences!
                  </p>
                  <Button onClick={() => setShowCreatePost(true)}>
                    Create Your First Post
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-6">
                {recommendedPosts.map((post) => (
                  <PostCard
                    key={post.id}
                    post={post}
                    onPostUpdate={handlePostUpdate}
                  />
                ))}
              </div>
            )}

            {/* End of Feed */}
            {recommendedPosts.length > 0 && (
              <div className="text-center py-8">
                <div className="flex items-center justify-center space-x-2 mb-2">
                  <Sparkles className="h-5 w-5 text-purple-500" />
                  <p className="text-muted-foreground">That's all for now!</p>
                  <Sparkles className="h-5 w-5 text-purple-500" />
                </div>
                <p className="text-sm text-muted-foreground">
                  Interact with posts to improve future recommendations
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </ResponsiveLayout>
  );
};

export default Feed;