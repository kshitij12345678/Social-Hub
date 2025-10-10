/**
 * Phase 5: Create Post Component
 * Instagram-like post creation with media upload
 */

import React, { useState, useRef } from 'react';
import { Camera, Image as ImageIcon, Video, X, MapPin, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { apiService, Post } from '@/services/apiService';

interface CreatePostProps {
  onPostCreated?: (newPost: Post) => void;
  onCancel?: () => void;
}

const CreatePost: React.FC<CreatePostProps> = ({ onPostCreated, onCancel }) => {
  const [caption, setCaption] = useState('');
  const [selectedMedia, setSelectedMedia] = useState<File | null>(null);
  const [mediaPreview, setMediaPreview] = useState<string | null>(null);
  const [mediaType, setMediaType] = useState<'image' | 'video' | null>(null);
  const [travelDate, setTravelDate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleMediaSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Check file size (50MB limit)
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      toast({
        title: "File too large",
        description: "Please select a file smaller than 50MB.",
        variant: "destructive",
      });
      return;
    }

    // Check file type
    const isImage = file.type.startsWith('image/');
    const isVideo = file.type.startsWith('video/');
    
    if (!isImage && !isVideo) {
      toast({
        title: "Invalid file type",
        description: "Please select an image or video file.",
        variant: "destructive",
      });
      return;
    }

    setSelectedMedia(file);
    setMediaType(isImage ? 'image' : 'video');

    // Create preview URL
    const previewUrl = URL.createObjectURL(file);
    setMediaPreview(previewUrl);
  };

  const handleRemoveMedia = () => {
    if (mediaPreview) {
      URL.revokeObjectURL(mediaPreview);
    }
    setSelectedMedia(null);
    setMediaPreview(null);
    setMediaType(null);
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!caption.trim()) {
      toast({
        title: "Caption required",
        description: "Please add a caption to your post.",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      // Create post with proper data structure including media file
      const newPost = await apiService.createPost({
        caption: caption.trim(),
        location_id: undefined, // Can be added later
        travel_date: travelDate || undefined,
        mediaFile: selectedMedia || undefined
      });

      toast({
        title: "Post created!",
        description: "Your post has been shared successfully.",
      });

      // Reset form
      setCaption('');
      setTravelDate('');
      handleRemoveMedia();

      // Notify parent component
      onPostCreated?.(newPost);

    } catch (error) {
      console.error('Failed to create post:', error);
      toast({
        title: "Error",
        description: "Failed to create post. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const openFileSelector = () => {
    fileInputRef.current?.click();
  };

  return (
    <Card className="w-full max-w-lg mx-auto mb-6">
      <CardContent className="p-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Create Post</h3>
            {onCancel && (
              <Button type="button" variant="ghost" size="sm" onClick={onCancel}>
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Caption Input */}
          <div className="space-y-2">
            <Label htmlFor="caption">Caption *</Label>
            <Textarea
              id="caption"
              placeholder="What's on your mind? Share your travel experience..."
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              className="min-h-20 resize-none"
              maxLength={2000}
            />
            <p className="text-xs text-muted-foreground text-right">
              {caption.length}/2000
            </p>
          </div>

          {/* Media Upload */}
          <div className="space-y-2">
            <Label>Media (Optional)</Label>
            
            {!selectedMedia ? (
              <div className="border-2 border-dashed border-border rounded-lg p-6 text-center">
                <div className="flex justify-center space-x-4 mb-4">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={openFileSelector}
                    className="flex items-center space-x-2"
                  >
                    <ImageIcon className="h-4 w-4" />
                    <span>Photo</span>
                  </Button>
                  
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={openFileSelector}
                    className="flex items-center space-x-2"
                  >
                    <Video className="h-4 w-4" />
                    <span>Video</span>
                  </Button>
                </div>
                
                <p className="text-sm text-muted-foreground">
                  Upload photos or videos to share your travel moments
                </p>
              </div>
            ) : (
              <div className="relative">
                {mediaType === 'video' ? (
                  <video
                    src={mediaPreview || ''}
                    className="w-full aspect-video object-cover rounded-lg"
                    controls
                  />
                ) : (
                  <img
                    src={mediaPreview || ''}
                    alt="Preview"
                    className="w-full aspect-video object-cover rounded-lg"
                  />
                )}
                
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  onClick={handleRemoveMedia}
                  className="absolute top-2 right-2"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,video/*"
              onChange={handleMediaSelect}
              className="hidden"
            />
          </div>

          {/* Travel Date */}
          <div className="space-y-2">
            <Label htmlFor="travelDate" className="flex items-center space-x-1">
              <Calendar className="h-4 w-4" />
              <span>Travel Date (Optional)</span>
            </Label>
            <Input
              id="travelDate"
              type="date"
              value={travelDate}
              onChange={(e) => setTravelDate(e.target.value)}
              max={new Date().toISOString().split('T')[0]} // Max date is today
            />
          </div>

          {/* Submit Button */}
          <div className="flex space-x-2">
            <Button
              type="submit"
              disabled={isSubmitting || !caption.trim()}
              className="flex-1"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Posting...
                </>
              ) : (
                'Share Post'
              )}
            </Button>
            
            {onCancel && (
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default CreatePost;