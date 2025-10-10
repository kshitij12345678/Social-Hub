/**
 * Share Dialog Component
 * For now uses hardcoded names, will be expanded later
 */

import React, { useState } from 'react';
import { Share, Users, MessageCircle, Copy, Link, Instagram, Twitter, Facebook } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';

interface ShareDialogProps {
  postId: number;
  onShare?: () => void;
  trigger?: React.ReactNode;
}

const ShareDialog: React.FC<ShareDialogProps> = ({ postId, onShare, trigger }) => {
  const { toast } = useToast();
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Hardcoded friends/contacts for now
  const hardcodedContacts = [
    {
      id: 1,
      name: 'Alex Johnson',
      username: '@alexj',
      avatar: '',
      status: 'online'
    },
    {
      id: 2,
      name: 'Sarah Wilson',
      username: '@sarahw',
      avatar: '',
      status: 'offline'
    },
    {
      id: 3,
      name: 'Mike Chen',
      username: '@mikechen',
      avatar: '',
      status: 'online'
    },
    {
      id: 4,
      name: 'Emma Davis',
      username: '@emmad',
      avatar: '',
      status: 'online'
    },
    {
      id: 5,
      name: 'David Rodriguez',
      username: '@davidr',
      avatar: '',
      status: 'offline'
    },
    {
      id: 6,
      name: 'Lisa Thompson',
      username: '@lisat',
      avatar: '',
      status: 'online'
    }
  ];

  const filteredContacts = hardcodedContacts.filter(contact =>
    contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contact.username.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getUserInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleShareToContact = (contact: any) => {
    toast({
      title: "Post shared!",
      description: `Shared with ${contact.name}`,
    });
    onShare?.();
    setIsOpen(false);
  };

  const handleCopyLink = () => {
    const postUrl = `${window.location.origin}/post/${postId}`;
    navigator.clipboard.writeText(postUrl);
    toast({
      title: "Link copied!",
      description: "Post link has been copied to clipboard",
    });
  };

  const handleSocialShare = (platform: string) => {
    const postUrl = `${window.location.origin}/post/${postId}`;
    const text = "Check out this amazing post from Social Hub!";
    
    let shareUrl = '';
    
    switch (platform) {
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(postUrl)}`;
        break;
      case 'facebook':
        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(postUrl)}`;
        break;
      case 'instagram':
        // Instagram doesn't support direct URL sharing, so just copy link
        handleCopyLink();
        return;
    }
    
    if (shareUrl) {
      window.open(shareUrl, '_blank', 'width=600,height=400');
    }
    
    toast({
      title: "Shared!",
      description: `Shared on ${platform.charAt(0).toUpperCase() + platform.slice(1)}`,
    });
    onShare?.();
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="ghost" size="sm">
            <Share className="h-4 w-4" />
          </Button>
        )}
      </DialogTrigger>
      
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Share className="h-5 w-5" />
            <span>Share Post</span>
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Social Media Sharing */}
          <div>
            <h4 className="text-sm font-medium mb-3 text-muted-foreground">Share on social media</h4>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSocialShare('instagram')}
                className="flex-1"
              >
                <Instagram className="h-4 w-4 mr-2" />
                Instagram
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSocialShare('twitter')}
                className="flex-1"
              >
                <Twitter className="h-4 w-4 mr-2" />
                Twitter
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSocialShare('facebook')}
                className="flex-1"
              >
                <Facebook className="h-4 w-4 mr-2" />
                Facebook
              </Button>
            </div>
          </div>

          {/* Copy Link */}
          <div>
            <h4 className="text-sm font-medium mb-3 text-muted-foreground">Copy link</h4>
            <Button
              variant="outline"
              onClick={handleCopyLink}
              className="w-full"
            >
              <Copy className="h-4 w-4 mr-2" />
              Copy post link
            </Button>
          </div>

          {/* Share with Friends */}
          <div>
            <h4 className="text-sm font-medium mb-3 text-muted-foreground flex items-center">
              <Users className="h-4 w-4 mr-2" />
              Share with friends
            </h4>
            
            {/* Search Friends */}
            <Input
              placeholder="Search friends..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="mb-3"
            />
            
            {/* Friends List */}
            <div className="max-h-48 overflow-y-auto space-y-2">
              {filteredContacts.length === 0 ? (
                <div className="text-center text-muted-foreground py-4">
                  <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No friends found</p>
                </div>
              ) : (
                filteredContacts.map((contact) => (
                  <div
                    key={contact.id}
                    className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50 cursor-pointer"
                    onClick={() => handleShareToContact(contact)}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="relative">
                        <Avatar className="h-10 w-10">
                          <AvatarImage src={contact.avatar} alt={contact.name} />
                          <AvatarFallback className="bg-primary text-primary-foreground text-sm">
                            {getUserInitials(contact.name)}
                          </AvatarFallback>
                        </Avatar>
                        <div className={`absolute -bottom-1 -right-1 h-3 w-3 rounded-full border-2 border-background ${
                          contact.status === 'online' ? 'bg-green-500' : 'bg-gray-400'
                        }`} />
                      </div>
                      
                      <div>
                        <p className="font-medium text-sm">{contact.name}</p>
                        <p className="text-xs text-muted-foreground">{contact.username}</p>
                      </div>
                    </div>
                    
                    <Button variant="ghost" size="sm">
                      <MessageCircle className="h-4 w-4" />
                    </Button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ShareDialog;