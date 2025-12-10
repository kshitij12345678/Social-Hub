import React, { useState, useEffect, useCallback } from 'react';
import { Send, Phone, Video, MoreVertical, Hash, Lock, MessageSquare, Reply, Smile, ThumbsUp, Heart, Laugh, Angry, Frown, Pin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { chatService, type ChatMessage, type ChatConversation } from '@/services/chat';
import { useToast } from '@/hooks/use-toast';

interface ChatWindowProps {
  selectedChannel: ChatConversation;
  isAuthenticated: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ selectedChannel, isAuthenticated }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const { toast } = useToast();

  // Common reaction emojis
  const reactionEmojis = [
    { emoji: '👍', icon: ThumbsUp, label: 'Like' },
    { emoji: '❤️', icon: Heart, label: 'Love' },
    { emoji: '😂', icon: Laugh, label: 'Laugh' },
    { emoji: '😮', icon: Frown, label: 'Surprised' },
    { emoji: '😢', icon: Frown, label: 'Sad' },
    { emoji: '😡', icon: Angry, label: 'Angry' },
    { emoji: '🔥', icon: Heart, label: 'Fire' },
    { emoji: '💯', icon: ThumbsUp, label: '100' }
  ];

  // Load messages for selected channel
  const loadMessages = useCallback(async () => {
    console.log('🔄 loadMessages called - selectedChannel:', selectedChannel, 'isAuthenticated:', isAuthenticated);
    
    if (!selectedChannel || !isAuthenticated) {
      console.log('❌ Early return - no channel or not authenticated');
      return;
    }

    try {
      setLoading(true);
      console.log('📡 Loading messages for channel:', selectedChannel.name);

      const channelIdentifier = selectedChannel.name || selectedChannel.id;
      const channelType = selectedChannel.type === 'private_group' ? 'group' : 'channel';

      console.log('🔍 Channel details:', { channelIdentifier, channelType });

      const channelMessages = await chatService.getRocketChatChannelMessages(
        channelIdentifier,
        channelType
      );

      console.log('📨 Raw channel messages received:', channelMessages);

      // Sort messages by timestamp (oldest first)
      const sortedMessages = channelMessages.sort(
        (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );

      // Add some test messages with different dates for testing
      if (sortedMessages.length === 0) {
        const now = new Date();
        const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        const dayBefore = new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000);
        
        sortedMessages.push(
          {
            id: 'test-1',
            text: 'This is a message from 2 days ago',
            user: { id: '1', username: 'test1', name: 'Test User 1' },
            timestamp: dayBefore.toISOString(),
            type: 'message',
            reactions: {},
            thread_count: 0,
            thread_messages: []
          },
          {
            id: 'test-2',
            text: 'This is a message from yesterday',
            user: { id: '2', username: 'test2', name: 'Test User 2' },
            timestamp: yesterday.toISOString(),
            type: 'message',
            reactions: {},
            thread_count: 0,
            thread_messages: []
          },
          {
            id: 'test-3',
            text: 'This is a message from today',
            user: { id: '3', username: 'test3', name: 'Test User 3' },
            timestamp: now.toISOString(),
            type: 'message',
            reactions: {},
            thread_count: 0,
            thread_messages: []
          }
        );
      }

      console.log('📋 Sorted messages:', sortedMessages);
      setMessages(sortedMessages);
      console.log(`✅ Loaded ${sortedMessages.length} messages for ${selectedChannel.name}`);
    } catch (error) {
      console.error('❌ Failed to load messages:', error);
      toast({
        title: "Error",
        description: `Failed to load messages from ${selectedChannel.name}`,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [selectedChannel, isAuthenticated, toast]);

  // Load messages when selected channel changes
  useEffect(() => {
    loadMessages();
  }, [loadMessages]);

  // Send message
  const handleSendMessage = useCallback(async () => {
    if (!newMessage.trim() || !selectedChannel || sending) return;

    try {
      setSending(true);
      
      // For private groups, use rocket_chat_group_id if available, otherwise normalize the name
      let channelIdentifier;
      if (selectedChannel.type === 'private_group') {
        // For private groups, use rocket_chat_group_id if available, otherwise normalize the name
        if ((selectedChannel as any).rocket_chat_group_id) {
          channelIdentifier = (selectedChannel as any).rocket_chat_group_id;
          console.log('🔍 Using rocket_chat_group_id for main message:', channelIdentifier);
        } else {
          // Fallback to normalized group name
          channelIdentifier = selectedChannel.name
            .toLowerCase()
            .replace(/[^a-z0-9]/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '');
          console.log('🔍 Using normalized group name for main message:', channelIdentifier);
        }
        
        console.log('🔍 Private group identifier:', { 
          rocket_chat_group_id: (selectedChannel as any).rocket_chat_group_id,
          name: selectedChannel.name,
          normalizedName: channelIdentifier,
          finalIdentifier: channelIdentifier 
        });
      } else {
        channelIdentifier = selectedChannel.name || selectedChannel.id;
      }
      
      const channelType = selectedChannel.type === 'private_group' ? 'group' : 'channel';

      console.log('🔍 Sending message to:', { channelIdentifier, channelType, selectedChannel });

      await chatService.sendRocketChatChannelMessage(
        channelIdentifier,
        newMessage,
        channelType
      );

      setNewMessage('');
      
      // Reload messages to show the new message
      await loadMessages();
      
      toast({
        title: "Message sent!",
        description: `Your message has been sent to ${selectedChannel.name}`,
      });
    } catch (error) {
      console.error('Failed to send message:', error);
      toast({
        title: "Error",
        description: `Failed to send message to ${selectedChannel.name}`,
        variant: "destructive",
      });
    } finally {
      setSending(false);
    }
  }, [newMessage, selectedChannel, sending, loadMessages, toast]);

  // Handle Enter key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle reaction toggle
  const handleReactionToggle = async (messageId: string, emoji: string) => {
    try {
      // Check if user already reacted with this emoji
      const message = messages.find(m => m.id === messageId);
      if (!message || !message.reactions) return;

      const hasReacted = message.reactions[emoji]?.includes('ankush1'); // Replace with actual current user
      
      if (hasReacted) {
        await chatService.removeReaction(messageId, emoji);
        toast({
          title: "Reaction removed",
          description: `Removed ${emoji} reaction`,
        });
      } else {
        await chatService.addReaction(messageId, emoji);
        toast({
          title: "Reaction added",
          description: `Added ${emoji} reaction`,
        });
      }
      
      // Reload messages to show updated reactions
      await loadMessages();
    } catch (error) {
      console.error('Failed to toggle reaction:', error);
      toast({
        title: "Error",
        description: "Failed to update reaction",
        variant: "destructive",
      });
    }
  };

  // Handle thread message send
  const handleSendThreadMessage = async (parentMessageId: string, text: string) => {
    try {
      // Use the same channel identifier logic as main message sending
      let channelIdentifier;
      let username: string | undefined = undefined;
      let conversationType: string | undefined = selectedChannel.type;
      
      if (selectedChannel.type === 'private_group') {
        // For private groups, use rocket_chat_group_id if available, otherwise normalize the name
        if ((selectedChannel as any).rocket_chat_group_id) {
          channelIdentifier = (selectedChannel as any).rocket_chat_group_id;
          console.log('🔍 Using rocket_chat_group_id for thread message:', channelIdentifier);
        } else {
          // Fallback to normalized group name
          channelIdentifier = selectedChannel.name
            .toLowerCase()
            .replace(/[^a-z0-9]/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '');
          console.log('🔍 Using normalized group name for thread message:', channelIdentifier);
        }
        
        console.log('🔍 Thread message - Private group identifier:', { 
          rocket_chat_group_id: (selectedChannel as any).rocket_chat_group_id,
          name: selectedChannel.name,
          normalizedName: channelIdentifier,
          finalIdentifier: channelIdentifier 
        });
      } else if (selectedChannel.type === 'direct_message') {
        // For direct messages, use other_user as username
        username = selectedChannel.other_user || '';
        channelIdentifier = selectedChannel.name || selectedChannel.id;
        console.log('🔍 Thread message - Direct message identifier:', { 
          username,
          conversationType: 'direct_message'
        });
      } else {
        channelIdentifier = selectedChannel.name || selectedChannel.id;
      }
      
      await chatService.sendThreadMessage(channelIdentifier, parentMessageId, text, username, conversationType);
      
      toast({
        title: "Thread message sent!",
        description: "Your reply has been sent",
      });
      
      // Reload messages to show the new thread message
      await loadMessages();
      
      // Also reload thread messages for this specific parent message
      try {
        console.log('🔄 Reloading thread messages for parent:', parentMessageId);
        const threadMessages = await chatService.getThreadMessages(parentMessageId);
        console.log('📨 Thread messages received:', threadMessages);
        setThreadMessages(prev => {
          const updated = {
            ...prev,
            [parentMessageId]: threadMessages.messages || []
          };
          console.log('🔄 Updated thread messages state:', updated);
          return updated;
        });
      } catch (error) {
        console.error('Failed to reload thread messages:', error);
      }
    } catch (error) {
      console.error('Failed to send thread message:', error);
      toast({
        title: "Error",
        description: "Failed to send thread message",
        variant: "destructive",
      });
    }
  };

  const handlePinMessage = async (messageId: string, messageText: string) => {
    try {
      const roomId = selectedChannel.id;
      const roomName = selectedChannel.name || selectedChannel.display_name || '';
      const roomType = selectedChannel.type === 'private_group' ? 'group' : 'channel';
      
      console.log('📌 Pinning message:', { messageId, roomId, roomName, roomType });
      
      const response = await fetch('http://localhost:8000/chat/pin-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          message_id: messageId,
          room_id: roomId,
          room_name: roomName,
          room_type: roomType,
          message_text: messageText
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to pin message');
      }
      
      toast({
        title: "Message pinned!",
        description: "The message has been pinned successfully",
      });
      
      // Reload messages to update pinned status
      await loadMessages();
    } catch (error) {
      console.error('Failed to pin message:', error);
      toast({
        title: "Error",
        description: "Failed to pin message",
        variant: "destructive",
      });
    }
  };

  const isPrivate = selectedChannel.type === 'private_group' || selectedChannel.is_private;
  const channelDisplayName = selectedChannel.display_name || selectedChannel.name;

  return (
    <Card className="h-full flex flex-col">
      {/* Chat Header */}
      <CardHeader className="pb-4 border-b flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center text-xl">
              {isPrivate ? <Lock className="h-4 w-4" /> : <Hash className="h-4 w-4" />}
            </div>
            <div>
              <h2 className="font-semibold">{channelDisplayName}</h2>
              <p className="text-sm text-muted-foreground">
                {isPrivate ? 'Private Group' : 'Rocket.Chat Channel'}
                {selectedChannel.member_count && ` • ${selectedChannel.member_count} members`}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button variant="ghost" size="sm" className="hover:bg-accent/10">
              <Phone className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" className="hover:bg-accent/10">
              <Video className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" className="hover:bg-accent/10">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      {/* Messages Area */}
      <CardContent className="flex-1 overflow-y-auto p-4 scrollbar-hide min-h-0 max-h-full">
        <div className="space-y-4 pb-4">
          {loading ? (
            <div className="text-center text-muted-foreground py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
              <p>Loading messages...</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No messages yet. Start a conversation!</p>
            </div>
          ) : (
            (() => {
              const messageElements: React.ReactNode[] = [];
              let lastDate: string | null = null;
              
              console.log('🗓️ Processing messages for date separators:', messages.length, 'messages');
              
              messages.forEach((message, index) => {
                const currentMessageDate = new Date(message.timestamp).toDateString();
                const showDateSeparator = currentMessageDate !== lastDate;
                
                console.log(`📅 Message ${index}: ${currentMessageDate}, lastDate: ${lastDate}, showSeparator: ${showDateSeparator}`);
                
                if (showDateSeparator) {
                  console.log(`✨ Adding date separator for: ${currentMessageDate}`);
                  messageElements.push(
                    <div key={`date-${message.id}`} className="flex items-center justify-center my-4">
                      <div className="flex-1 border-t border-muted"></div>
                      <span className="px-3 text-xs text-muted-foreground bg-background">
                        {new Date(message.timestamp).toLocaleDateString([], { 
                          weekday: 'long',
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })}
                      </span>
                      <div className="flex-1 border-t border-muted"></div>
                    </div>
                  );
                  lastDate = currentMessageDate;
                }
                
                messageElements.push(
                  <MessageComponent
                    key={message.id}
                    message={message}
                    isThreadMessage={false}
                    onReactionToggle={handleReactionToggle}
                    onSendThreadMessage={handleSendThreadMessage}
                    onPinMessage={handlePinMessage}
                    reactionEmojis={reactionEmojis}
                    showReactionPicker={showReactionPicker}
                    setShowReactionPicker={setShowReactionPicker}
                  />
                );
              });
              
              console.log('📋 Total elements created:', messageElements.length);
              return messageElements;
            })()
          )}
          
          {sending && (
            <div className="text-center text-muted-foreground py-2">
              <div className="inline-flex items-center space-x-2">
                <div className="animate-spin w-4 h-4 border-2 border-primary border-t-transparent rounded-full"></div>
                <span>Sending...</span>
              </div>
            </div>
          )}
        </div>
      </CardContent>

      {/* Message Input */}
      <div className="p-4 border-t flex-shrink-0">
        <div className="flex items-center space-x-2">
          <div className="flex-1 relative">
            <Input
              placeholder={`Message ${channelDisplayName}...`}
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={sending}
              className="pr-12"
            />
          </div>
          <Button 
            onClick={handleSendMessage}
            disabled={!newMessage.trim() || sending}
            size="sm"
            className="transition-spring hover:scale-105"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default ChatWindow;