/**
 * Phase 5: Instagram-like Post Card Component
 * Displays posts with media, interactions, and real-time updates
 */

import React, { useState } from 'react';
import { Heart, MessageCircle, Share, MoreHorizontal, MapPin } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Post, apiService } from '@/services/apiService';
import { formatDistanceToNow } from 'date-fns';
import CommentSection from './comment-section';
import ShareDialog from './share-dialog';

interface PostCardProps {
  post: Post;
  onPostUpdate?: (updatedPost: Partial<Post>) => void;
}

const PostCard: React.FC<PostCardProps> = ({ post, onPostUpdate }) => {
  const [isLiked, setIsLiked] = useState(post.is_liked_by_user);
  const [likesCount, setLikesCount] = useState(post.likes_count);
  const [commentsCount, setCommentsCount] = useState(post.comments_count);
  const [sharesCount, setSharesCount] = useState(post.shares_count);
  const [isLiking, setIsLiking] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const { toast } = useToast();

  const handleLike = async () => {
    if (isLiking) return;
    
    // Optimistic update
    const newIsLiked = !isLiked;
    const newLikesCount = newIsLiked ? likesCount + 1 : likesCount - 1;
    
    setIsLiked(newIsLiked);
    setLikesCount(newLikesCount);
    setIsLiking(true);

    try {
      const response = await apiService.toggleLike(post.id);
      
      // Update with server response
      setLikesCount(response.likes_count);
      setIsLiked(response.is_liked);
      
      // Notify parent component
      onPostUpdate?.({
        id: post.id,
        likes_count: response.likes_count,
        is_liked_by_user: response.is_liked,
      });
      
    } catch (error) {
      // Revert optimistic update on error
      setIsLiked(!newIsLiked);
      setLikesCount(likesCount);
      
      toast({
        title: "Error",
        description: "Failed to update like. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLiking(false);
    }
  };



  const formatTimeAgo = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return 'Recently';
    }
  };

  const getUserInitials = (fullName: string) => {
    return fullName
      .split(' ')
      .map(name => name[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Card className="w-full max-w-lg mx-auto mb-6 overflow-hidden">
      {/* Post Header */}
      <div className="flex items-center justify-between p-4">
        <div className="flex items-center space-x-3">
          <Avatar className="h-10 w-10">
            <AvatarImage 
              src={post.user.profile_picture_url} 
              alt={post.user.full_name}
            />
            <AvatarFallback className="bg-primary text-primary-foreground">
              {getUserInitials(post.user.full_name)}
            </AvatarFallback>
          </Avatar>
          
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <h3 className="font-semibold text-sm">{post.user.full_name}</h3>
              {post.user.location && (
                <Badge variant="secondary" className="text-xs">
                  <MapPin className="h-3 w-3 mr-1" />
                  {post.user.location}
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {formatTimeAgo(post.created_at)}
            </p>
          </div>
        </div>
        
        <Button variant="ghost" size="sm">
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </div>

      {/* Post Media */}
      {post.media_url && (
        <div className="relative">
          {post.media_type === 'video' ? (
            <video 
              className="w-full aspect-square object-cover"
              controls
              preload="metadata"
            >
              <source src={post.media_url} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          ) : (
            <img 
              src={post.media_url} 
              alt="Post content"
              className="w-full aspect-square object-cover"
              loading="lazy"
            />
          )}
        </div>
      )}

      <CardContent className="p-4">
        {/* Action Buttons */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLike}
              disabled={isLiking}
              className={`p-0 hover:bg-transparent ${
                isLiked ? 'text-red-500' : 'text-muted-foreground'
              }`}
            >
              <Heart 
                className={`h-6 w-6 ${isLiked ? 'fill-current' : ''}`} 
              />
            </Button>
            
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setShowComments(!showComments)}
              className={`p-0 hover:bg-transparent ${showComments ? 'text-primary' : 'text-muted-foreground'}`}
            >
              <MessageCircle className="h-6 w-6" />
            </Button>
            
            <ShareDialog 
              postId={post.id}
              onShare={() => {
                setSharesCount(prev => prev + 1);
                onPostUpdate?.({
                  id: post.id,
                  shares_count: sharesCount + 1,
                });
              }}
              trigger={
                <Button
                  variant="ghost"
                  size="sm"
                  className="p-0 text-muted-foreground hover:bg-transparent"
                >
                  <Share className="h-6 w-6" />
                </Button>
              }
            />
          </div>
        </div>

        {/* Likes Count */}
        {likesCount > 0 && (
          <p className="font-semibold text-sm mb-2">
            {likesCount.toLocaleString()} {likesCount === 1 ? 'like' : 'likes'}
          </p>
        )}

        {/* Caption */}
        <div className="mb-2">
          <span className="font-semibold text-sm mr-2">{post.user.full_name}</span>
          <span className="text-sm">{post.caption}</span>
        </div>

        {/* Comments */}
        {commentsCount > 0 && (
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setShowComments(true)}
            className="p-0 text-muted-foreground hover:bg-transparent text-sm"
          >
            View all {commentsCount} {commentsCount === 1 ? 'comment' : 'comments'}
          </Button>
        )}

        {/* Travel Date */}
        {post.travel_date && (
          <p className="text-xs text-muted-foreground mt-2">
            📅 {new Date(post.travel_date).toLocaleDateString()}
          </p>
        )}
      </CardContent>

      {/* Comment Section */}
      <CommentSection
        postId={post.id}
        isVisible={showComments}
        onCommentAdded={() => {
          setCommentsCount(prev => prev + 1);
          onPostUpdate?.({
            id: post.id,
            comments_count: commentsCount + 1,
          });
        }}
      />
    </Card>
  );
};

export default PostCard;