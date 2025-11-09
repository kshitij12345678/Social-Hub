/**
 * Profile Post Card Component with Edit/Delete Menu
 * Instagram-style post card with 3-dot menu for user's own posts
 */

import React, { useState } from 'react';
import { Heart, MessageCircle, Share, MoreHorizontal, MapPin, Edit3, Trash2, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { Post, apiService } from '@/services/apiService';
import { formatDistanceToNow } from 'date-fns';
import CommentSection from './comment-section';
import ShareDialog from './share-dialog';

interface ProfilePostCardProps {
  post: Post;
  onPostUpdate?: (updatedPost: Partial<Post>) => void;
  onPostDelete?: (postId: number) => void;
  currentUserId: number;
}

const ProfilePostCard: React.FC<ProfilePostCardProps> = ({ 
  post, 
  onPostUpdate, 
  onPostDelete,
  currentUserId 
}) => {
  const [isLiked, setIsLiked] = useState(post.is_liked_by_user);
  const [likesCount, setLikesCount] = useState(post.likes_count);
  const [commentsCount, setCommentsCount] = useState(post.comments_count);
  const [sharesCount, setSharesCount] = useState(post.shares_count);
  const [isLiking, setIsLiking] = useState(false);
  const [showComments, setShowComments] = useState(false);
  
  // Edit/Delete states
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [editCaption, setEditCaption] = useState(post.caption || '');
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  
  const { toast } = useToast();

  // Check if current user owns this post
  const isOwner = post.user.id === currentUserId;

  const handleLike = async () => {
    if (isLiking) return;
    
    const newIsLiked = !isLiked;
    const newLikesCount = newIsLiked ? likesCount + 1 : likesCount - 1;
    
    setIsLiked(newIsLiked);
    setLikesCount(newLikesCount);
    setIsLiking(true);

    try {
      const response = await apiService.toggleLike(post.id);
      setLikesCount(response.likes_count);
      setIsLiked(response.is_liked);
      
      onPostUpdate?.({
        id: post.id,
        likes_count: response.likes_count,
        is_liked_by_user: response.is_liked,
      });
      
    } catch (error) {
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

  const handleEditPost = async () => {
    if (isUpdating) return;
    
    setIsUpdating(true);
    
    try {
      const updateData: { caption?: string } = {};
      
      if (editCaption !== post.caption) {
        updateData.caption = editCaption;
      }
      
      // Check if there are any changes to make
      if (Object.keys(updateData).length === 0) {
        toast({
          title: "No Changes",
          description: "No changes were made to update.",
        });
        setShowEditDialog(false);
        setIsUpdating(false);
        return;
      }
      
      const updatedPost = await apiService.updatePost(post.id, updateData);
      
      // Update local state immediately
      if (updateData.caption !== undefined) {
        setEditCaption(updateData.caption);
      }
      
      onPostUpdate?.(updatedPost);
      setShowEditDialog(false);
      
      toast({
        title: "Success",
        description: "Post updated successfully!",
      });
      
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update post. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDeletePost = async () => {
    if (isDeleting) return;
    
    setIsDeleting(true);
    
    try {
      await apiService.deletePost(post.id);
      
      onPostDelete?.(post.id);
      setShowDeleteDialog(false);
      
      toast({
        title: "Success",
        description: "Post deleted successfully!",
      });
      
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete post. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsDeleting(false);
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
    <>
      <Card className="w-full max-w-lg mx-auto mb-6 overflow-hidden">
        {/* Post Header */}
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-3">
            <Avatar className="h-10 w-10">
              <AvatarImage 
                src={post.user.profile_picture_url} 
                alt={post.user.full_name}
              />
              <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
                {getUserInitials(post.user.full_name)}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="font-semibold text-sm">{post.user.full_name}</p>
              {post.location_id && (
                <div className="flex items-center text-xs text-muted-foreground">
                  <MapPin className="h-3 w-3 mr-1" />
                  <span>Location</span>
                </div>
              )}
            </div>
          </div>
          
          {/* Show 3-dot menu only for post owner */}
          {isOwner && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setShowEditDialog(true)}>
                  <Edit3 className="h-4 w-4 mr-2" />
                  Edit post
                </DropdownMenuItem>
                <DropdownMenuItem 
                  onClick={() => setShowDeleteDialog(true)}
                  className="text-red-600 focus:text-red-600"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete post
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
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
              />
            )}
          </div>
        )}

        {/* Post Actions */}
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={handleLike}
                disabled={isLiking}
                className="p-0 h-auto hover:bg-transparent"
              >
                <Heart 
                  className={`h-6 w-6 ${isLiked ? 'fill-red-500 text-red-500' : 'text-gray-700'} transition-colors`}
                />
              </Button>
              
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setShowComments(!showComments)}
                className="p-0 h-auto hover:bg-transparent"
              >
                <MessageCircle className="h-6 w-6 text-gray-700" />
              </Button>
              
              <Button variant="ghost" size="sm" className="p-0 h-auto hover:bg-transparent">
                <Share className="h-6 w-6 text-gray-700" />
              </Button>
            </div>
          </div>

          {/* Engagement Stats */}
          <div className="space-y-1 mb-2">
            {likesCount > 0 && (
              <p className="text-sm font-semibold">
                {likesCount.toLocaleString()} {likesCount === 1 ? 'like' : 'likes'}
              </p>
            )}
          </div>

          {/* Caption */}
          {post.caption && (
            <div className="mb-2">
              <p className="text-sm">
                <span className="font-semibold mr-2">{post.user.full_name}</span>
                {post.caption}
              </p>
            </div>
          )}

          {/* Comments Count */}
          {commentsCount > 0 && (
            <button 
              onClick={() => setShowComments(!showComments)}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors mb-2"
            >
              View all {commentsCount} {commentsCount === 1 ? 'comment' : 'comments'}
            </button>
          )}

          {/* Timestamp */}
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {formatTimeAgo(post.created_at)}
          </p>
        </div>

        {/* Comments Section */}
        {showComments && (
          <CommentSection 
            postId={post.id}
            isVisible={showComments}
            onCommentAdded={() => {
              setCommentsCount(prev => prev + 1);
            }}
          />
        )}
      </Card>

      {/* Edit Post Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Post</DialogTitle>
            <DialogDescription>
              Update your post caption.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="caption">Caption</Label>
              <Textarea
                id="caption"
                placeholder="What's on your mind?"
                value={editCaption}
                onChange={(e) => setEditCaption(e.target.value)}
                className="min-h-[100px]"
              />
            </div>
          </div>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setShowEditDialog(false)}
              disabled={isUpdating}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleEditPost}
              disabled={isUpdating}
            >
              {isUpdating && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Update Post
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Delete Post</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this post? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setShowDeleteDialog(false)}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button 
              variant="destructive"
              onClick={handleDeletePost}
              disabled={isDeleting}
            >
              {isDeleting && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ProfilePostCard;