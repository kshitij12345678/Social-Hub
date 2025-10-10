/**
 * Instagram-style Comment Section Component
 * Features: nested comments, replies, like functionality
 */

import React, { useState, useEffect } from 'react';
import { Heart, MessageCircle, MoreHorizontal, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useToast } from '@/hooks/use-toast';
import { apiService, Comment } from '@/services/apiService';
import { useAuth } from '@/contexts/AuthContext';
import { formatDistanceToNow } from 'date-fns';

interface CommentSectionProps {
  postId: number;
  isVisible: boolean;
  onCommentAdded?: () => void;
}

interface CommentItemProps {
  comment: Comment;
  onReply: (commentId: number, username: string) => void;
}

const CommentItem: React.FC<CommentItemProps> = ({ comment, onReply }) => {
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);

  const getUserInitials = (fullName: string) => {
    return fullName
      .split(' ')
      .map(name => name[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const formatTimeAgo = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return 'Recently';
    }
  };

  return (
    <div className="flex space-x-3 py-2">
      <Avatar className="h-8 w-8">
        <AvatarImage 
          src={comment.user.profile_picture_url} 
          alt={comment.user.full_name}
        />
        <AvatarFallback className="bg-muted text-xs">
          {getUserInitials(comment.user.full_name)}
        </AvatarFallback>
      </Avatar>
      
      <div className="flex-1 min-w-0">
        <div className="bg-muted rounded-2xl px-3 py-2">
          <div className="flex items-center space-x-2 mb-1">
            <span className="font-semibold text-sm">{comment.user.full_name}</span>
          </div>
          <p className="text-sm text-foreground break-words">{comment.comment_text}</p>
        </div>
        
        <div className="flex items-center space-x-4 mt-1 px-3">
          <button 
            className="text-xs text-muted-foreground hover:text-foreground"
            onClick={() => setIsLiked(!isLiked)}
          >
            {formatTimeAgo(comment.created_at)}
          </button>
          
          <button 
            className={`text-xs hover:text-foreground ${isLiked ? 'text-red-500 font-semibold' : 'text-muted-foreground'}`}
            onClick={() => setIsLiked(!isLiked)}
          >
            Like
          </button>
          
          <button 
            className="text-xs text-muted-foreground hover:text-foreground"
            onClick={() => onReply(comment.id, comment.user.full_name)}
          >
            Reply
          </button>
          
          {likesCount > 0 && (
            <span className="text-xs text-muted-foreground">
              {likesCount} {likesCount === 1 ? 'like' : 'likes'}
            </span>
          )}
        </div>
        
        {/* TODO: Nested replies functionality will be added later */}
      </div>
    </div>
  );
};

const CommentSection: React.FC<CommentSectionProps> = ({ 
  postId, 
  isVisible, 
  onCommentAdded 
}) => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [replyTo, setReplyTo] = useState<{ id: number; username: string } | null>(null);

  // Load comments when section becomes visible
  useEffect(() => {
    if (isVisible && comments.length === 0) {
      loadComments();
    }
  }, [isVisible, postId]);

  const loadComments = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.getComments(postId);
      setComments(response.comments);
    } catch (error) {
      console.error('Failed to load comments:', error);
      toast({
        title: "Error",
        description: "Failed to load comments",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const commentText = replyTo 
        ? `@${replyTo.username} ${newComment}` 
        : newComment;
        
      const response = await apiService.addComment(postId, commentText);
      
      // Add new comment to the list
      setComments(prev => [response, ...prev]);
      setNewComment('');
      setReplyTo(null);
      onCommentAdded?.();
      
      toast({
        title: "Comment added!",
        description: "Your comment has been posted.",
      });
      
    } catch (error) {
      console.error('Failed to add comment:', error);
      toast({
        title: "Error",
        description: "Failed to post comment. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReply = (commentId: number, username: string) => {
    setReplyTo({ id: commentId, username });
    setNewComment('');
  };

  const getUserInitials = (fullName: string) => {
    return fullName
      .split(' ')
      .map(name => name[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  if (!isVisible) return null;

  return (
    <div className="border-t border-muted">
      {/* Comments List */}
      <div className="max-h-96 overflow-y-auto p-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
          </div>
        ) : comments.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <MessageCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No comments yet</p>
            <p className="text-sm">Be the first to comment!</p>
          </div>
        ) : (
          <div className="space-y-1">
            {comments.map((comment) => (
              <CommentItem 
                key={comment.id} 
                comment={comment}
                onReply={handleReply}
              />
            ))}
          </div>
        )}
      </div>

      {/* Comment Input */}
      <div className="border-t border-muted p-4">
        {replyTo && (
          <div className="flex items-center space-x-2 mb-2 p-2 bg-muted rounded-md">
            <span className="text-sm text-muted-foreground">
              Replying to <span className="font-semibold">@{replyTo.username}</span>
            </span>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setReplyTo(null)}
              className="h-4 w-4 p-0"
            >
              ×
            </Button>
          </div>
        )}
        
        <form onSubmit={handleSubmitComment} className="flex items-center space-x-3">
          <Avatar className="h-8 w-8">
            <AvatarImage 
              src={user?.profile_picture_url} 
              alt={user?.full_name}
            />
            <AvatarFallback className="bg-primary text-primary-foreground text-xs">
              {user?.full_name ? getUserInitials(user.full_name) : 'U'}
            </AvatarFallback>
          </Avatar>
          
          <div className="flex-1 relative">
            <Input
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder={replyTo ? `Reply to @${replyTo.username}...` : "Add a comment..."}
              className="pr-12 rounded-full border-muted"
              disabled={isSubmitting}
            />
            <Button
              type="submit"
              variant="ghost"
              size="sm"
              disabled={!newComment.trim() || isSubmitting}
              className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0 rounded-full"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CommentSection;