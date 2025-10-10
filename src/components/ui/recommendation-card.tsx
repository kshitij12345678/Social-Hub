import React, { useState, useEffect } from 'react';
import { Sparkles, TrendingUp, Users, Brain, RefreshCw, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/apiService';
import PostCard from '@/components/ui/post-card';

interface RecommendationCardProps {
  onPostsLoad?: (posts: any[]) => void;
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({ onPostsLoad }) => {
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();
  
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendationInfo, setRecommendationInfo] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);

  const loadRecommendations = async () => {
    if (!isAuthenticated) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Try to get personalized recommendations
      const response = await apiService.getRecommendedPosts(6);
      
      setRecommendations(response.recommendations);
      setRecommendationInfo(response.recommendation_info);
      
      // Pass posts to parent component if callback provided
      if (onPostsLoad) {
        onPostsLoad(response.recommendations);
      }
      
      toast({
        title: "✨ Recommendations Loaded",
        description: `Got ${response.total_count} personalized recommendations using ${response.recommendation_info.algorithm}`,
      });
      
    } catch (err) {
      console.error('Failed to load recommendations:', err);
      
      // Fallback to popular posts
      try {
        const fallbackResponse = await apiService.getPopularPosts(6);
        setRecommendations(fallbackResponse.posts);
        setRecommendationInfo(fallbackResponse.recommendation_info);
        
        if (onPostsLoad) {
          onPostsLoad(fallbackResponse.posts);
        }
        
        toast({
          title: "📈 Popular Posts Loaded",
          description: "Showing popular posts as fallback",
        });
        
      } catch (fallbackErr) {
        console.error('Failed to load popular posts:', fallbackErr);
        setError('Failed to load recommendations. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const loadStats = async () => {
    if (!isAuthenticated) return;
    
    try {
      const statsResponse = await apiService.getRecommendationStats();
      setStats(statsResponse);
    } catch (err) {
      console.error('Failed to load recommendation stats:', err);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadRecommendations();
      loadStats();
    }
  }, [isAuthenticated]);

  const getAlgorithmIcon = (algorithm: string) => {
    switch (algorithm) {
      case 'hybrid':
        return <Brain className="w-4 h-4" />;
      case 'collaborative_filtering':
        return <Users className="w-4 h-4" />;
      case 'content_based_filtering':
        return <Sparkles className="w-4 h-4" />;
      case 'popularity_based':
        return <TrendingUp className="w-4 h-4" />;
      default:
        return <Sparkles className="w-4 h-4" />;
    }
  };

  const getAlgorithmColor = (algorithm: string) => {
    switch (algorithm) {
      case 'hybrid':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'collaborative_filtering':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'content_based_filtering':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'popularity_based':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Sparkles className="w-5 h-5 text-purple-600" />
            Recommended for You
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={loadRecommendations}
            disabled={isLoading}
            className="flex items-center gap-1"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
        
        {recommendationInfo && (
          <div className="flex flex-wrap gap-2 mt-2">
            <Badge 
              variant="outline" 
              className={`flex items-center gap-1 ${getAlgorithmColor(recommendationInfo.algorithm)}`}
            >
              {getAlgorithmIcon(recommendationInfo.algorithm)}
              {recommendationInfo.algorithm === 'hybrid' ? 'AI Hybrid' : 
               recommendationInfo.algorithm === 'collaborative_filtering' ? 'Similar Users' :
               recommendationInfo.algorithm === 'content_based_filtering' ? 'Your Interests' :
               'Popular Posts'}
            </Badge>
            
            {recommendationInfo.personalized && (
              <Badge variant="outline" className="bg-pink-100 text-pink-800 border-pink-200">
                Personalized
              </Badge>
            )}
          </div>
        )}
      </CardHeader>

      <CardContent className="pt-0">
        {error && (
          <Alert className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {isLoading && (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex space-x-3">
                <Skeleton className="h-16 w-16 rounded-lg" />
                <div className="space-y-2 flex-1">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                  <Skeleton className="h-3 w-1/4" />
                </div>
              </div>
            ))}
          </div>
        )}

        {!isLoading && !error && recommendations.length > 0 && (
          <div className="space-y-4">
            {recommendations.slice(0, 3).map((post, index) => (
              <div 
                key={post.post_id} 
                className="flex items-start space-x-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors cursor-pointer"
              >
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-pink-400 rounded-lg flex items-center justify-center text-white font-medium">
                    {index + 1}
                  </div>
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 line-clamp-2">
                    {post.caption}
                  </p>
                  <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                    <span>by {post.author_username}</span>
                    {post.location && (
                      <>
                        <span>•</span>
                        <span>{post.location}</span>
                      </>
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${getAlgorithmColor(post.algorithm)}`}
                    >
                      {getAlgorithmIcon(post.algorithm)}
                      {post.algorithm === 'collaborative_filtering' ? 'Similar Users' :
                       post.algorithm === 'content_based_filtering' ? 'Your Interests' :
                       'Popular'}
                    </Badge>
                    <span className="text-xs text-gray-500">
                      Score: {typeof post.popularity_score === 'number' ? post.popularity_score.toFixed(1) : 'N/A'}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1 italic">
                    {post.recommendation_reason}
                  </p>
                </div>
              </div>
            ))}
            
            {recommendations.length > 3 && (
              <div className="text-center pt-2">
                <Button variant="ghost" size="sm" className="text-purple-600">
                  View all {recommendations.length} recommendations
                </Button>
              </div>
            )}
          </div>
        )}

        {!isLoading && !error && recommendations.length === 0 && (
          <div className="text-center py-6">
            <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500">No recommendations available yet.</p>
            <p className="text-sm text-gray-400 mt-1">
              Interact with more posts to get personalized recommendations!
            </p>
          </div>
        )}

        {stats && (
          <div className="mt-4 pt-4 border-t">
            <div className="flex justify-between text-xs text-gray-500">
              <span>Your Interactions: {stats.interaction_stats?.total_interactions || 0}</span>
              <span>System: Ready for AI</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default RecommendationCard;