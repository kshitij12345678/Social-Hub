import React, { useState, useEffect, useCallback, useRef } from 'react';
import ResponsiveLayout from '@/components/layout/responsive-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { type ChatConversation, type ChatMessage } from '@/services/chat';
import { chatService as rocketChatService } from '@/services/chat';
import { useToast } from '@/hooks/use-toast';
import { Hash, Lock, MessageCircle, Users, User, Search, Send, Smile, Reply, Paperclip, Image, File, Mic, Video, MoreHorizontal, UserPlus, Pin, Trash2, Phone, Share2, Edit } from 'lucide-react';
import { UserSearch } from './UserSearch';
import { UserSearchResult } from '@/services/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

// Helper function to format message timestamp
const formatMessageTime = (timestamp: string) => {
  const messageDate = new Date(timestamp);
  const now = new Date();
  const isToday = messageDate.toDateString() === now.toDateString();
  const isYesterday = messageDate.toDateString() === new Date(now.getTime() - 24 * 60 * 60 * 1000).toDateString();
  
  if (isToday) {
    return messageDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } else if (isYesterday) {
    return `Yesterday ${messageDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  } else {
    return messageDate.toLocaleDateString([], { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }
};

interface EnhancedMessagesWidgetProps {
  openGroup?: {
    id: number;
    name: string;
    rocket_chat_group_id?: string;
    type: string;
  };
}

const EnhancedMessagesWidget: React.FC<EnhancedMessagesWidgetProps> = ({ openGroup }) => {
  console.log('🎯 EnhancedMessagesWidget component is rendering');
  
  // Tab navigation state
  const [activeTab, setActiveTab] = useState<'all' | 'groups' | 'dms'>('all');
  
  // Pinned messages state
  const [pinnedMessages, setPinnedMessages] = useState<ChatMessage[]>([]);
  const [pinnedMessageIds, setPinnedMessageIds] = useState<Set<string>>(new Set());
  
  // Chat data state
  const [channels, setChannels] = useState<ChatConversation[]>([]);
  const [groups, setGroups] = useState<ChatConversation[]>([]);
  const [directMessages, setDirectMessages] = useState<ChatConversation[]>([]);
  const [filteredDMs, setFilteredDMs] = useState<ChatConversation[]>([]);
  
  // Selected conversation and messages
  const [selectedConversation, setSelectedConversation] = useState<ChatConversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  
  // State persistence
  const [isInitialized, setIsInitialized] = useState(false);
  
  // Loading states
  const [loadingChannels, setLoadingChannels] = useState(false);
  const [loadingGroups, setLoadingGroups] = useState(false);
  const [loadingDMs, setLoadingDMs] = useState(false);
  const [loadingFilteredDMs, setLoadingFilteredDMs] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  
  // Message input and sending
  const [newMessage, setNewMessage] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);
  
  // File sharing state
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  
  // Typing indicators
  const [typingUsers, setTypingUsers] = useState<{ [conversationId: string]: string[] }>({});
  const [isTyping, setIsTyping] = useState(false);
  
  // Thread functionality
  const [threadMessages, setThreadMessages] = useState<{ [parentId: string]: ChatMessage[] }>({});
  const [loadingThread, setLoadingThread] = useState<string | null>(null);
  const [openThreads, setOpenThreads] = useState<Set<string>>(new Set());
  const [threadReplyText, setThreadReplyText] = useState<{ [parentId: string]: string }>({});
  const [sendingThreadReply, setSendingThreadReply] = useState<string | null>(null);
  
  // Reactions
  const [showReactionPicker, setShowReactionPicker] = useState<string | null>(null);
  
  // Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<ChatMessage[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  
  // User search
  const [showUserSearch, setShowUserSearch] = useState(false);
  
  // Forward message state
  const [showForwardDialog, setShowForwardDialog] = useState(false);
  const [forwardingMessageId, setForwardingMessageId] = useState<string | null>(null);
  const [forwardSearchQuery, setForwardSearchQuery] = useState('');
  const [forwardSearchResults, setForwardSearchResults] = useState<ChatConversation[]>([]);
  const [forwardingTo, setForwardingTo] = useState<ChatConversation | null>(null);
  const [isForwarding, setIsForwarding] = useState(false);
  
  // Edit message state
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editingMessageText, setEditingMessageText] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  
  const { isAuthenticated, user, isLoading: authLoading } = useAuth();
  const { toast } = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Helper function to render text with clickable links
  const renderMessageContent = (text: string): React.ReactNode => {
    if (!text) return text;
    
    // Custom components for markdown rendering
    const components = {
      p: ({ children }: any) => <p className="mb-2 text-black dark:text-white">{children}</p>,
      h1: ({ children }: any) => <h1 className="text-2xl font-bold mb-2 mt-3 text-black dark:text-white">{children}</h1>,
      h2: ({ children }: any) => <h2 className="text-xl font-bold mb-2 mt-2 text-black dark:text-white">{children}</h2>,
      h3: ({ children }: any) => <h3 className="text-lg font-bold mb-2 mt-2 text-black dark:text-white">{children}</h3>,
      h4: ({ children }: any) => <h4 className="font-bold mb-1 mt-1 text-black dark:text-white">{children}</h4>,
      strong: ({ children }: any) => <strong className="font-bold text-black dark:text-white">{children}</strong>,
      em: ({ children }: any) => <em className="italic text-black dark:text-white">{children}</em>,
      code: ({ inline, children }: any) => 
        inline 
          ? <code className="bg-gray-700 text-white px-2 py-1 rounded text-sm font-mono whitespace-pre-wrap border border-gray-600">{children}</code>
          : <code className="block bg-gray-700 text-white p-3 rounded text-sm font-mono overflow-x-auto mb-2 border border-gray-600 whitespace-pre-wrap">{children}</code>,
      pre: ({ children }: any) => <pre className="bg-gray-700 text-white p-3 rounded mb-2 overflow-x-auto text-sm border border-gray-600 whitespace-pre-wrap">{children}</pre>,
      blockquote: ({ children }: any) => <blockquote className="border-l-4 border-blue-400 pl-3 italic my-2 text-black dark:text-white bg-gray-800 py-2 px-2">{children}</blockquote>,
      ul: ({ children }: any) => <ul className="list-disc list-inside mb-2 space-y-1 text-black dark:text-white">{children}</ul>,
      ol: ({ children }: any) => <ol className="list-decimal list-inside mb-2 space-y-1 text-black dark:text-white">{children}</ol>,
      li: ({ children }: any) => <li className="ml-2 text-black dark:text-white">{children}</li>,
      a: ({ href, children }: any) => (
        <a 
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline break-all"
        >
          {children}
        </a>
      ),
      hr: () => <hr className="my-3 border-gray-500" />
    };
    
    return (
      <div className="max-w-none text-black dark:text-white">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm, remarkBreaks]}
          components={components}
        >
          {text}
        </ReactMarkdown>
      </div>
    );
  };


  // Save selected conversation to localStorage
  const saveSelectedConversation = (conversation: ChatConversation | null) => {
    if (conversation) {
      localStorage.setItem('selectedConversation', JSON.stringify({
        id: conversation.id,
        type: conversation.type,
        name: conversation.name,
        display_name: conversation.display_name,
        other_user: conversation.other_user
      }));
    } else {
      localStorage.removeItem('selectedConversation');
    }
  };

  // Restore selected conversation from localStorage
  const restoreSelectedConversation = (conversations: ChatConversation[]) => {
    try {
      const saved = localStorage.getItem('selectedConversation');
      if (saved) {
        const savedConversation = JSON.parse(saved);
        const foundConversation = conversations.find(conv => 
          conv.id === savedConversation.id && 
          conv.type === savedConversation.type
        );
        if (foundConversation) {
          console.log('🔄 Restoring selected conversation:', foundConversation);
          setSelectedConversation(foundConversation);
          return foundConversation;
        }
      }
    } catch (error) {
      console.error('Error restoring selected conversation:', error);
    }
    return null;
  };

  // Load pinned messages for a conversation
  const loadPinnedMessages = async (roomId: string) => {
    if (!roomId) return;
    
    try {
      console.log('📌 Loading pinned messages with room_id:', roomId);
      
      const response = await fetch(`http://localhost:8000/chat/pinned-messages?room_id=${encodeURIComponent(roomId)}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('📌 Loaded pinned messages:', data);
        
        if (data.pinned_messages && Array.isArray(data.pinned_messages)) {
          // Convert pinned messages to ChatMessage format
          const pinnedMsgs: ChatMessage[] = data.pinned_messages.map((pm: Record<string, unknown>) => ({
            id: pm.message_id as string,
            text: pm.message_text as string,
            content: pm.message_text as string,
            sender: 'System',
            timestamp: pm.pinned_at as string,
            user: { id: 'system', username: 'system', name: 'System' },
            reactions: {},
            thread_count: 0
          }));
          
          setPinnedMessages(pinnedMsgs);
          setPinnedMessageIds(new Set(data.pinned_messages.map((pm: Record<string, unknown>) => pm.message_id as string)));
        }
      }
    } catch (error) {
      console.error('Failed to load pinned messages:', error);
    }
  };

  const loadChannelsAndDMs = useCallback(async () => {
    console.log('🔄 Loading channels, groups and DMs...');
    console.log('🔍 User info:', { isAuthenticated, user: user?.email });
    console.log('🔍 Token in localStorage:', !!localStorage.getItem('access_token'));
    
    setLoadingChannels(true);
    setLoadingGroups(true);
    setLoadingDMs(true);
    
    try {
      // Use the same methods as the chat widget
      console.log('🔄 Loading channels with messages...');
      const channelsData = await rocketChatService.getChannelsWithMessages();
      console.log('📺 Channels loaded:', channelsData);
      setChannels(channelsData);
      
      console.log('🔄 Loading groups with messages...');
      const groupsData = await rocketChatService.getGroupsWithMessages();
      console.log('👥 Groups loaded:', groupsData);
      console.log('👥 Groups details:', groupsData.map(g => ({ name: g.name, type: g.type, id: g.id })));
      setGroups(groupsData);
      
      console.log('🔄 Loading direct messages...');
      const dmsData = await rocketChatService.getDirectMessagesWithMessages();
      console.log('💬 DMs loaded:', dmsData);
      console.log('💬 DMs count:', dmsData.length);
      setDirectMessages(dmsData);
      
      // Combine all conversations and try to restore selected conversation
      const allConversations = [...channelsData, ...groupsData, ...dmsData];
      
      // Check if we need to open a specific group from navigation
      let conversationToSelect = null;
      
      if (openGroup) {
        console.log('🎯 Looking for openGroup:', openGroup);
        // Find the group in the loaded conversations
        conversationToSelect = allConversations.find(conv => 
          conv.type === 'private_group' && 
          (conv.id === openGroup.id.toString() || conv.name === openGroup.name)
        );
        
        if (conversationToSelect) {
          console.log('✅ Found group to open:', conversationToSelect);
        } else {
          console.log('⚠️ Group not found in conversations, creating temporary conversation');
          // Create a temporary conversation for the new group
          conversationToSelect = {
            id: openGroup.id.toString(),
            name: openGroup.name,
            display_name: openGroup.name,
            type: 'private_group' as const,
            unread_count: 0,
            last_message: null,
            last_message_time: null
          };
        }
      } else {
        // Try to restore selected conversation from localStorage
        conversationToSelect = restoreSelectedConversation(allConversations);
      }
      
      // If we have a conversation to select, load its messages
      if (conversationToSelect) {
        console.log('🔄 Loading messages for selected conversation:', conversationToSelect);
        setSelectedConversation(conversationToSelect);
        saveSelectedConversation(conversationToSelect);
        setLoadingMessages(true);

        try {
          let conversationMessages: ChatMessage[] = [];
          
          if (conversationToSelect.type === 'direct_message' && conversationToSelect.other_user) {
            // Use the conversation name (Rocket.Chat username) instead of display name
            const username = conversationToSelect.name || conversationToSelect.other_user;
            console.log('Loading DM messages for username:', username, 'display_name:', conversationToSelect.other_user);
            conversationMessages = await rocketChatService.getDirectMessageMessages(username);
          } else {
            console.log('Loading channel messages for:', conversationToSelect.name || conversationToSelect.id);
            conversationMessages = await rocketChatService.getRocketChatChannelMessages(
              conversationToSelect.name || conversationToSelect.id,
              conversationToSelect.type === 'private_group' ? 'group' : 'channel'
            );
          }
          
          console.log('Loaded messages count:', conversationMessages.length);
          
          // Load pinned messages for this conversation
          // For DMs, use the composite room_id format
          const roomIdForPinned = conversationToSelect.type === 'direct_message'
            ? `dm:${conversationToSelect.name || conversationToSelect.other_user || ''}`
            : conversationToSelect.id;
          loadPinnedMessages(roomIdForPinned);
          
          // Debug: Check which messages are thread messages
          const threadMsgs = conversationMessages.filter(msg => msg.is_thread_message);
          console.log('Thread messages found:', threadMsgs.length);
          threadMsgs.forEach((msg, index) => {
            console.log(`Thread message ${index}:`, {
              id: msg.id,
              text: msg.text,
              is_thread_message: msg.is_thread_message,
              sender: msg.sender,
              user: msg.user
            });
          });
          
          // Simplified thread message detection - only check explicit metadata
          const isThreadMessage = (msg: ChatMessage): boolean => {
            // Only filter messages that have explicit thread metadata
            if (msg.is_thread_message === true || msg.thread_ts || msg.tmid) {
              return true;
            }
            return false;
          };
          
          // Filter out thread messages from the main message list (only those with explicit thread metadata)
          const filteredMessages = conversationMessages.filter(msg => {
            if (isThreadMessage(msg)) {
              return false;
            }
            return true;
          });
          console.log('Total messages loaded:', conversationMessages.length);
          console.log('Filtered messages (excluding thread messages):', filteredMessages.length);
          setMessages(filteredMessages);
        } catch (error) {
          console.error('Failed to load messages:', error);
          toast({
            title: "Error",
            description: "Failed to load messages",
            variant: "destructive",
          });
        } finally {
          setLoadingMessages(false);
        }
      }
      
      setIsInitialized(true);
    } catch (error) {
      console.error('❌ Failed to load channels, groups and DMs:', error);
      console.error('❌ Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      });
      setIsInitialized(true);
    } finally {
      setLoadingChannels(false);
      setLoadingGroups(false);
      setLoadingDMs(false);
    }
  }, [isAuthenticated, user?.email, openGroup, toast]);

  // Removed auto-scroll to bottom when messages change
  // useEffect(() => {
  //   scrollToBottom();
  // }, [messages]);

  // Load conversations when component mounts
  useEffect(() => {
    console.log('🔍 EnhancedMessagesWidget useEffect - isAuthenticated:', isAuthenticated, 'isInitialized:', isInitialized, 'openGroup:', openGroup);
    if (isAuthenticated && !isInitialized) {
      console.log('🔄 Starting to load channels and DMs...');
      loadChannelsAndDMs();
    }
  }, [isAuthenticated, isInitialized, openGroup, loadChannelsAndDMs]);


  // Filter DMs based on messages
  useEffect(() => {
    let isMounted = true;
    console.log('🔍 DM Filter Effect - directMessages:', directMessages);
    if (directMessages.length > 0) {
      setLoadingFilteredDMs(true);
      // Simply use all DMs without filtering by messages
      setFilteredDMs(directMessages);
      setLoadingFilteredDMs(false);
    } else {
      console.log('❌ No direct messages to filter');
      setFilteredDMs([]);
      setLoadingFilteredDMs(false);
    }
    return () => { isMounted = false; };
  }, [directMessages]);

  const handleConversationSelect = async (conversation: ChatConversation) => {
    console.log('Selecting conversation:', conversation);
    setSelectedConversation(conversation);
    
    // Save the selected conversation to localStorage
    saveSelectedConversation(conversation);
    setLoadingMessages(true);

    try {
      let conversationMessages: ChatMessage[] = [];
      
      if (conversation.type === 'direct_message' && conversation.other_user) {
        // Use the conversation name (Rocket.Chat username) instead of display name
        const username = conversation.name || conversation.other_user;
        console.log('Loading DM messages for username:', username, 'display_name:', conversation.other_user);
        conversationMessages = await rocketChatService.getDirectMessageMessages(username);
      } else {
        console.log('Loading channel messages for:', conversation.name || conversation.id);
        conversationMessages = await rocketChatService.getRocketChatChannelMessages(
          conversation.name || conversation.id,
          conversation.type === 'private_group' ? 'group' : 'channel'
        );
      }
      
      console.log('Loaded messages count:', conversationMessages.length);
      
      // Load pinned messages for this conversation
      // For DMs, use the composite room_id format
      const roomIdForPinned = conversation.type === 'direct_message'
        ? `dm:${conversation.name || conversation.other_user || ''}`
        : conversation.id;
      loadPinnedMessages(roomIdForPinned);
      
      // Debug: Check which messages are thread messages
      const threadMessages = conversationMessages.filter(msg => msg.is_thread_message);
      console.log('Thread messages found:', threadMessages.length);
      threadMessages.forEach((msg, index) => {
        console.log(`Thread message ${index}:`, {
          id: msg.id,
          text: msg.text,
          is_thread_message: msg.is_thread_message,
          sender: msg.sender,
          user: msg.user
        });
      });
      
      // Simplified thread message detection - only check explicit metadata
      const isThreadMessage = (msg: any): boolean => {
        // Only filter messages that have explicit thread metadata
        if (msg.is_thread_message === true || msg.thread_ts || msg.tmid) {
          return true;
        }
        return false;
      };
      
      // Filter out thread messages from the main message list (only those with explicit thread metadata)
      const filteredMessages = conversationMessages.filter(msg => {
        if (isThreadMessage(msg)) {
          return false;
        }
        return true;
      });
      console.log('Total messages loaded:', conversationMessages.length);
      console.log('Filtered messages (excluding thread messages):', filteredMessages.length);
      setMessages(filteredMessages);
    } catch (error) {
      console.error('Failed to load messages:', error);
      toast({
        title: "Error",
        description: "Failed to load messages",
        variant: "destructive",
      });
    } finally {
      setLoadingMessages(false);
    }
  };

  // File handling functions
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    console.log('DEBUG: Files selected:', files.length, files.map(f => ({ name: f.name, size: f.size })));
    
    const validFiles = files.filter(file => {
      const maxSize = 10 * 1024 * 1024; // 10MB limit
      return file.size <= maxSize;
    });
    
    if (validFiles.length !== files.length) {
      toast({
        title: "File size limit exceeded",
        description: "Some files were too large (max 10MB per file)",
        variant: "destructive"
      });
    }
    
    console.log('DEBUG: Valid files:', validFiles.length, validFiles.map(f => ({ name: f.name, size: f.size })));
    setSelectedFiles(prev => {
      const newFiles = [...prev, ...validFiles];
      console.log('DEBUG: Total selected files:', newFiles.length);
      return newFiles;
    });
  };

  // Typing indicator functions
  const handleTypingStart = () => {
    if (!isTyping && selectedConversation) {
      setIsTyping(true);
      // In a real implementation, you'd send a typing event to the server
      console.log('User started typing...');
    }
  };

  const handleTypingStop = () => {
    if (isTyping) {
      setIsTyping(false);
      // In a real implementation, you'd send a stop typing event to the server
      console.log('User stopped typing...');
    }
  };

  const handleSendMessage = async () => {
    if ((!newMessage.trim() && selectedFiles.length === 0) || sendingMessage || !selectedConversation) return;

    const messageContent = newMessage;
    const filesToUpload = [...selectedFiles]; // Copy files before clearing state
    console.log('DEBUG: Sending message:', { 
      messageContent, 
      selectedConversation, 
      files: filesToUpload.length,
      fileNames: filesToUpload.map(f => f.name),
      fileSizes: filesToUpload.map(f => f.size),
      selectedFilesBeforeClear: selectedFiles.length
    });
    
    setNewMessage('');
    setSendingMessage(true);
    
    // Don't clear selectedFiles yet - we need them for upload

    try {
      // Handle file uploads if any files are selected
      let uploadedFiles: any[] = [];
      if (filesToUpload.length > 0) {
        console.log('DEBUG: Starting file upload for', filesToUpload.length, 'files');
        try {
          const formData = new FormData();
          filesToUpload.forEach((file, index) => {
            console.log('DEBUG: Adding file to FormData:', file.name, file.size, file.type);
            formData.append(`file_${index}`, file);
          });
          
          const token = localStorage.getItem('access_token');
          console.log('DEBUG: Token from localStorage:', token ? 'Present' : 'Missing');
          console.log('DEBUG: Sending FormData to upload endpoint');
          
          const uploadResponse = await fetch('/api/rocket-chat/upload-files', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
            body: formData,
          });
          
          console.log('DEBUG: Upload response status:', uploadResponse.status);
          console.log('DEBUG: Upload response headers:', Object.fromEntries(uploadResponse.headers.entries()));
          
          if (uploadResponse.ok) {
            const uploadResult = await uploadResponse.json();
            uploadedFiles = uploadResult.files || [];
            console.log('DEBUG: Files uploaded successfully:', uploadedFiles);
          } else {
            const errorText = await uploadResponse.text();
            console.error('File upload failed:', uploadResponse.status, errorText);
            console.error('DEBUG: Full error response:', {
              status: uploadResponse.status,
              statusText: uploadResponse.statusText,
              headers: Object.fromEntries(uploadResponse.headers.entries()),
              body: errorText
            });
            toast({
              title: "File upload failed",
              description: `Upload failed with status ${uploadResponse.status}: ${errorText}`,
              variant: "destructive",
            });
          }
        } catch (error) {
          console.error('Error uploading files:', error);
          toast({
            title: "File upload error",
            description: `Upload error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            variant: "destructive",
          });
        }
      }

      // Capture the real message ID from the send response
      let realMessageId: string | undefined;
      const tempMessageId = Date.now().toString();

      if (selectedConversation.type === 'direct_message' && selectedConversation.other_user) {
        // Use the conversation name (Rocket.Chat username) for sending DMs
        const username = selectedConversation.name || selectedConversation.other_user;
        console.log('🔍 DM Message Debug:', {
          conversationType: selectedConversation.type,
          conversationName: selectedConversation.name,
          otherUser: selectedConversation.other_user,
          username: username,
          messageContent: messageContent,
          attachments: uploadedFiles
        });
        const dmResponse = await rocketChatService.sendDirectMessage(username, messageContent, uploadedFiles);
        console.log('📨 DM Response:', dmResponse);
        
        // If we got a real message ID from the backend, use it
        if (dmResponse.message_id) {
          console.log('✅ Got message ID from DM response:', dmResponse.message_id);
          realMessageId = dmResponse.message_id;
        }
      } else {
        // For private groups, use the rocket_chat_group_id if available, otherwise use name
        let channelIdentifier;
        if (selectedConversation.type === 'private_group') {
          // For private groups, use rocket_chat_group_id if available, otherwise normalize the name
          if ((selectedConversation as any).rocket_chat_group_id) {
            channelIdentifier = (selectedConversation as any).rocket_chat_group_id;
            console.log('🔍 Using rocket_chat_group_id for main message:', channelIdentifier);
          } else {
            // Fallback to normalized group name
            channelIdentifier = selectedConversation.name
              .toLowerCase()
              .replace(/[^a-z0-9]/g, '-')
              .replace(/-+/g, '-')
              .replace(/^-|-$/g, '');
            console.log('🔍 Using normalized group name for main message:', channelIdentifier);
          }
          
          console.log('🔍 Private group identifier:', { 
            rocket_chat_group_id: (selectedConversation as any).rocket_chat_group_id,
            name: selectedConversation.name,
            normalizedName: channelIdentifier,
            finalIdentifier: channelIdentifier 
          });
        } else {
          channelIdentifier = selectedConversation.name || selectedConversation.id;
        }
        
        console.log('DEBUG: Calling sendRocketChatChannelMessage with:', {
          channelIdentifier: channelIdentifier,
          text: messageContent,
          channelType: selectedConversation.type === 'private_group' ? 'group' : 'channel',
          attachments: uploadedFiles
        });
        const channelResponse = await rocketChatService.sendRocketChatChannelMessage(
          channelIdentifier,
          messageContent,
          selectedConversation.type === 'private_group' ? 'group' : 'channel',
          uploadedFiles
        );
        console.log('📤 Channel Response:', channelResponse);
        
        // If we got a real message ID from the backend, use it
        if (channelResponse.message_id) {
          console.log('✅ Got message ID from channel response:', channelResponse.message_id);
          realMessageId = channelResponse.message_id;
        }
      }
      
      // Add the sent message to the messages array instead of reloading
      const newMessageObj: ChatMessage = {
        id: realMessageId || tempMessageId, // Use real ID if available, otherwise temporary
        text: messageContent,
        content: messageContent,
        user: {
          id: user?.id?.toString() || '',
          username: user?.email?.split('@')[0] || user?.name || 'You',
          name: user?.name || 'You'
        },
        sender: user?.email?.split('@')[0] || user?.name || 'You',
        timestamp: new Date().toISOString(),
        type: 'message',
        isOwn: true,
        attachments: uploadedFiles
      };
      
      console.log('Adding sent message to UI:', newMessageObj);
      setMessages(prev => {
        const updated = [...prev, newMessageObj];
        console.log('Updated messages count:', updated.length);
        return updated;
      });
      
      // Show success message with file count
      if (uploadedFiles.length > 0) {
        toast({
          title: "Message sent",
          description: `Message sent with ${uploadedFiles.length} file(s)`,
        });
      } else if (messageContent.trim()) {
        toast({
          title: "Message sent",
          description: "Message sent successfully",
        });
      }
      
      // Clear selected files after successful upload/send
      setSelectedFiles([]);
      
      // If this was a DM, refresh the DM list to ensure it appears in the DM section
      if (selectedConversation.type === 'direct_message') {
        console.log('🔄 Refreshing DM list after sending message...');
        try {
          const refreshedDMs = await rocketChatService.getDirectMessagesWithMessages();
          console.log('💬 Refreshed DMs:', refreshedDMs);
          setDirectMessages(refreshedDMs);
        } catch (error) {
          console.error('Failed to refresh DM list:', error);
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      console.error('Error details:', error);
      
      // Extract more detailed error information
      let errorMessage = 'Unknown error';
      if (error instanceof Error) {
        errorMessage = error.message;
        // If the error message is empty or just "Failed to send message:", try to get more details
        if (errorMessage === 'Failed to send message:' || errorMessage === 'Failed to send message') {
          errorMessage = 'Failed to send message. Please check your connection and try again.';
        }
      }
      
      // If error message is still empty or contains "Empty error message", retry fetching messages
      // as the message might have been sent successfully despite the error response
      if (!errorMessage || errorMessage.includes('Empty error message')) {
        console.log('Detected possible successful send with error response, attempting to refresh messages...');
        try {
          // Wait a moment then refresh messages
          await new Promise(resolve => setTimeout(resolve, 1000));
          if (selectedConversation) {
            const refreshedMessages = await rocketChatService.getRocketChatChannelMessages(
              selectedConversation.id || selectedConversation.name || '',
              selectedConversation.type === 'private_group' ? 'group' : 'channel'
            );
            setMessages(refreshedMessages);
            toast({
              title: "Success",
              description: "Message sent successfully",
            });
            return; // Exit without showing error
          }
        } catch (refreshError) {
          console.error('Failed to refresh messages:', refreshError);
        }
      }
      
      toast({
        title: "Error",
        description: `Failed to send message: ${errorMessage}`,
        variant: "destructive",
      });
      // Clear selected files even on error
      setSelectedFiles([]);
    } finally {
      setSendingMessage(false);
    }
  };

  const handleReactionToggle = async (messageId: string, emoji: string) => {
    try {
      console.log('Toggling reaction for message:', messageId, 'emoji:', emoji);
      
      const currentUser = user?.email?.split('@')[0] || user?.name || 'You';
      console.log('Current user:', currentUser);
      
      // Find the message - could be top-level or thread message
      let message = messages.find(msg => msg.id === messageId);
      let isThreadMessage = false;
      let parentMessageId = '';
      
      // If not found in top-level, search in thread messages
      if (!message) {
        for (const msg of messages) {
          const threadMsg = msg.thread_messages?.find(tm => tm.id === messageId);
          if (threadMsg) {
            message = threadMsg;
            isThreadMessage = true;
            parentMessageId = msg.id;
            break;
          }
        }
      }
      
      console.log('Found message:', message, 'isThreadMessage:', isThreadMessage);
      
      const currentReactions = message?.reactions || {};
      
      // OPTIMISTIC UPDATE: Update UI immediately
      setMessages(prev => prev.map(msg => {
        if (isThreadMessage && msg.id === parentMessageId) {
          // Update thread message reactions
          return {
            ...msg,
            thread_messages: msg.thread_messages?.map(threadMsg => {
              if (threadMsg.id === messageId) {
                const threadReactions = threadMsg.reactions || {};
                const currentUsers = threadReactions[emoji] || [];
                
                // Toggle reaction
                const newUsers = currentUsers.includes(currentUser) 
                  ? currentUsers.filter(u => u !== currentUser)
                  : [...currentUsers, currentUser];
                
                // Remove emoji if no users left
                const newReactions = { ...threadReactions };
                if (newUsers.length === 0) {
                  delete newReactions[emoji];
                } else {
                  newReactions[emoji] = newUsers;
                }
                
                console.log('Updated thread reaction optimistically:', newReactions);
                return { ...threadMsg, reactions: newReactions };
              }
              return threadMsg;
            })
          };
        } else if (msg.id === messageId) {
          // Update top-level message reactions
          const msgReactions = msg.reactions || {};
          const currentUsers = msgReactions[emoji] || [];
          
          // Toggle reaction
          const newUsers = currentUsers.includes(currentUser) 
            ? currentUsers.filter(u => u !== currentUser)
            : [...currentUsers, currentUser];
          
          // Remove emoji if no users left
          const newReactions = { ...msgReactions };
          if (newUsers.length === 0) {
            delete newReactions[emoji];
          } else {
            newReactions[emoji] = newUsers;
          }
          
          console.log('Updated top-level reaction optimistically:', newReactions);
          return { ...msg, reactions: newReactions };
        }
        return msg;
      }));
      
      // ALSO UPDATE threadMessages if this is a thread message that's been fetched
      if (isThreadMessage && parentMessageId && threadMessages[parentMessageId]) {
        setThreadMessages(prev => ({
          ...prev,
          [parentMessageId]: prev[parentMessageId].map(msg => {
            if (msg.id === messageId) {
              const msgReactions = msg.reactions || {};
              const currentUsers = msgReactions[emoji] || [];
              
              // Toggle reaction
              const newUsers = currentUsers.includes(currentUser) 
                ? currentUsers.filter(u => u !== currentUser)
                : [...currentUsers, currentUser];
              
              // Remove emoji if no users left
              const newReactions = { ...msgReactions };
              if (newUsers.length === 0) {
                delete newReactions[emoji];
              } else {
                newReactions[emoji] = newUsers;
              }
              
              console.log('Updated threadMessages state reaction optimistically:', newReactions);
              return { ...msg, reactions: newReactions };
            }
            return msg;
          })
        }));
      }
      
      // THEN call the API
      await rocketChatService.toggleReaction(messageId, emoji, currentReactions);
    } catch (error) {
      console.error('Failed to toggle reaction:', error);
      // Optionally: revert the optimistic update on error
      // You could reload messages here if needed
    }
  };

  const handleLoadThread = async (parentMessageId: string) => {
    if (openThreads.has(parentMessageId)) {
      setOpenThreads(prev => {
        const newSet = new Set(prev);
        newSet.delete(parentMessageId);
        return newSet;
      });
      return;
    }

    setLoadingThread(parentMessageId);
    try {
      const result = await rocketChatService.getThreadMessages(parentMessageId);
      setThreadMessages(prev => ({ ...prev, [parentMessageId]: result.messages }));
      setOpenThreads(prev => new Set([...prev, parentMessageId]));
    } catch (error) {
      console.error('Failed to load thread messages:', error);
    } finally {
      setLoadingThread(null);
    }
  };

  const handleSendThreadReply = async (parentMessageId: string) => {
    const replyText = threadReplyText[parentMessageId];
    if (!replyText?.trim() || sendingThreadReply === parentMessageId) {
      console.log('🚫 Thread reply blocked:', { 
        hasText: !!replyText?.trim(), 
        isSending: sendingThreadReply === parentMessageId,
        replyText: replyText 
      });
      return;
    }

    console.log('🚀 Starting thread reply:', { 
      parentMessageId, 
      replyText, 
      selectedConversation: selectedConversation?.name,
      conversationType: selectedConversation?.type
    });
    
    setSendingThreadReply(parentMessageId);
    
    try {
      // Use the same channel identifier logic as main message sending
      let roomIdentifier;
      if (selectedConversation.type === 'private_group') {
        // For private groups, use rocket_chat_group_id if available, otherwise normalize the name
        if ((selectedConversation as any).rocket_chat_group_id) {
          roomIdentifier = (selectedConversation as any).rocket_chat_group_id;
          console.log('🔍 Using rocket_chat_group_id for thread message:', roomIdentifier);
        } else {
          // Fallback to normalized group name
          roomIdentifier = selectedConversation.name
            .toLowerCase()
            .replace(/[^a-z0-9]/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '');
          console.log('🔍 Using normalized group name for thread message:', roomIdentifier);
        }
        
        console.log('🔍 Thread message - Private group identifier:', { 
          rocket_chat_group_id: (selectedConversation as any).rocket_chat_group_id,
          name: selectedConversation.name,
          normalizedName: roomIdentifier,
          finalIdentifier: roomIdentifier 
        });
      } else {
        roomIdentifier = selectedConversation?.name || selectedConversation?.id;
      }
      
      console.log('DEBUG: Using room identifier:', roomIdentifier);
      console.log('DEBUG: Parent message ID:', parentMessageId);
      console.log('DEBUG: Reply text:', replyText);
      const threadResponse = await rocketChatService.sendThreadMessage(roomIdentifier || '', parentMessageId, replyText);
      console.log('DEBUG: Thread message response:', threadResponse);
      
      setThreadReplyText(prev => ({ ...prev, [parentMessageId]: '' }));
      
      // Capture the real message ID if available
      let realThreadMessageId: string | undefined;
      if (threadResponse && typeof threadResponse === 'object') {
        const message = (threadResponse as any).message;
        if (message && typeof message === 'object' && message._id) {
          realThreadMessageId = message._id;
          console.log('✅ Got real thread message ID from backend:', realThreadMessageId);
        }
      }
      
      // Add the thread message to local state immediately (optimistic update)
      console.log('🔄 Adding thread message to local state optimistically');
      const tempThreadMessageId = Date.now().toString();
      const newThreadMessage: ChatMessage = {
        id: realThreadMessageId || tempThreadMessageId, // Use real ID if available
        _id: realThreadMessageId, // Store Rocket.Chat ID
        text: replyText,
        content: replyText,
        user: {
          id: user?.id || 'current-user',
          username: user?.email?.split('@')[0] || user?.name || 'You',
          name: user?.name || 'You',
          email: user?.email || '',
        },
        timestamp: new Date().toISOString(),
        is_thread_message: true,
        thread_ts: parentMessageId,
        tmid: parentMessageId,
        isOwn: true,
      };
      
      // Add to thread messages state
      setThreadMessages(prev => ({
        ...prev,
        [parentMessageId]: [...(prev[parentMessageId] || []), newThreadMessage]
      }));
      
      // Also update the parent message's thread_count if it exists
      setMessages(prev => prev.map(msg => {
        if (msg.id === parentMessageId) {
          console.log('✅ Updating parent message with new thread message');
          return {
            ...msg,
            thread_count: (msg.thread_count || 0) + 1,
            thread_messages: msg.thread_messages ? [...msg.thread_messages, newThreadMessage] : [newThreadMessage]
          };
        }
        return msg;
      }));
      
      console.log('✅ Thread message added to local state');
      
      // Note: Using optimistic updates instead of server reload to avoid race conditions
      
      console.log('✅ Thread reply sent successfully!');
      toast({
        title: "Thread message sent!",
        description: "Your reply has been sent",
      });
    } catch (error) {
      console.error('❌ Failed to send thread reply:', error);
      console.error('❌ Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined,
        parentMessageId,
        replyText,
        selectedConversation: selectedConversation?.name
      });
      
      toast({
        title: "Error",
        description: "Failed to send thread message. Please try again.",
        variant: "destructive",
      });
    } finally {
      console.log('🔄 Cleaning up thread reply state for:', parentMessageId);
      setSendingThreadReply(null);
    }
  };

  // Handle user search selection
  const handleUserSelect = async (selectedUser: UserSearchResult) => {
    console.log('Selected user for DM:', selectedUser);
    
    try {
      // Derive username from email (before @ symbol)
      const username = selectedUser.email.split('@')[0];
      
      // Create a new DM conversation with the selected user
      const newDMConversation: ChatConversation = {
        id: `dm-${selectedUser.id}`,
        name: username, // Use the derived username
        display_name: selectedUser.full_name,
        type: 'direct_message',  // Use 'direct_message' to match the message sending logic
        other_user: selectedUser.full_name, // Use full name to match backend format
        unread_count: 0,
        last_message: null,
        last_message_time: null
      };
      
      // Add to DMs list if not already present
      setDirectMessages(prev => {
        const exists = prev.some(dm => dm.other_user === selectedUser.full_name);
        if (!exists) {
          console.log('Adding new DM conversation:', newDMConversation);
          return [newDMConversation, ...prev];
        }
        console.log('DM conversation already exists for user:', selectedUser.full_name);
        return prev;
      });
      
      // Select the conversation
      console.log('Selecting conversation:', newDMConversation);
      await handleConversationSelect(newDMConversation);
      
      toast({
        title: "Direct Message Started",
        description: `Started a conversation with ${selectedUser.full_name}`,
      });
      
    } catch (error) {
      console.error('Error starting DM:', error);
      toast({
        title: "Error",
        description: "Failed to start direct message. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Get conversations based on active tab
  const getConversations = () => {
    console.log('🔍 getConversations called:', {
      activeTab,
      channels: channels.length,
      groups: groups.length,
      directMessages: directMessages.length,
      filteredDMs: filteredDMs.length
    });
    
    switch (activeTab) {
      case 'all': {
        // All tab should only show merged Groups and DMs content
        const generalChannel = channels.find(ch => ch.name === 'general');
        const groupsWithGeneral = generalChannel ? [generalChannel, ...groups] : groups;
        return [...groupsWithGeneral, ...filteredDMs];
      }
      case 'groups': {
        // Include the general channel as it's the main group conversation
        const generalChannelForGroups = channels.find(ch => ch.name === 'general');
        const groupsWithGeneralForGroups = generalChannelForGroups ? [generalChannelForGroups, ...groups] : groups;
        return groupsWithGeneralForGroups;
      }
      case 'dms':
        return filteredDMs;
      default:
        return [];
    }
  };

  const conversations = getConversations();
  const filteredConversations = conversations.filter(conv => {
    // Basic search filter
    const matchesSearch = conv.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conv.display_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conv.other_user?.toLowerCase().includes(searchQuery.toLowerCase());
    
    // For DMs, exclude if the other user is the same as current user
    if (conv.type === 'direct_message') {
      const currentUsername = user?.email?.split('@')[0];
      if (conv.other_user === currentUsername) {
        return false;
      }
    }
    
    return matchesSearch;
  });

  // Debug logging for conversations
  console.log('🔍 EnhancedMessagesWidget - Conversations:', {
    activeTab,
    channels: channels.length,
    groups: groups.length,
    directMessages: directMessages.length,
    filteredDMs: filteredDMs.length,
    conversations: conversations.length,
    filteredConversations: filteredConversations.length,
    searchQuery,
    groupsData: groups.map(g => ({ id: g.id, name: g.name, type: g.type, display_name: g.display_name }))
  });
  
  // Debug the actual conversations array
  console.log('🔍 filteredConversations array:', filteredConversations.map(conv => ({
    id: conv.id,
    name: conv.name,
    type: conv.type,
    display_name: conv.display_name,
    other_user: conv.other_user
  })));

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <ResponsiveLayout>
        <div className="max-w-6xl mx-auto h-[calc(100vh-120px)] flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Checking authentication...</p>
          </div>
        </div>
      </ResponsiveLayout>
    );
  }

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <ResponsiveLayout>
        <div className="max-w-6xl mx-auto h-[calc(100vh-120px)] flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Authentication Required</h2>
            <p className="text-muted-foreground mb-6">Please log in to access Rocket.Chat channels.</p>
            <Button onClick={() => window.location.href = '/login'}>
              Go to Login
            </Button>
          </div>
        </div>
      </ResponsiveLayout>
    );
  }

  return (
    <ResponsiveLayout>
      <div className="w-full h-[calc(100vh-120px)] p-4">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 h-full">
          {/* Conversations List Sidebar */}
          <div className="md:col-span-4 lg:col-span-3">
            <Card className="h-full">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold mb-3">Messages</h2>
                
                {/* Tab Navigation */}
                <div className="flex border-b border-gray-200 dark:border-gray-700 mb-4">
                  <button
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === 'all'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                    onClick={() => setActiveTab('all')}
                  >
                    All
                  </button>
                  <button
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === 'groups'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                    onClick={() => setActiveTab('groups')}
                  >
                    Groups
                  </button>
                  <button
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === 'dms'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                    onClick={() => setActiveTab('dms')}
                  >
                    DM's
                  </button>
                </div>

                {/* Search */}
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search messages..."
                      value={searchQuery}
                      onChange={async (e) => {
                        const query = e.target.value;
                        setSearchQuery(query);
                        
                        if (query.trim().length >= 2) {
                          setIsSearching(true);
                          setShowSearchResults(true);
                          try {
                            const results = await rocketChatService.searchMessages(query, 50);
                            setSearchResults(results.messages || []);
                          } catch (error) {
                            console.error('Search failed:', error);
                            setSearchResults([]);
                          } finally {
                            setIsSearching(false);
                          }
                        } else if (query.trim().length === 0) {
                          setShowSearchResults(false);
                          setSearchResults([]);
                        }
                      }}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && searchQuery.trim().length >= 2) {
                          // Trigger search
                        }
                      }}
                      className="pl-10"
                    />
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowUserSearch(true)}
                    className="flex items-center gap-2"
                  >
                    <UserPlus className="h-4 w-4" />
                    New DM
                  </Button>
                </div>
              </div>

              {/* Conversations List or Search Results */}
              <ScrollArea className="h-[calc(100vh-300px)]">
                <div className="p-4 space-y-2">
                  {showSearchResults ? (
                    // Show search results
                    <>
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-medium text-sm text-gray-700">Search Results</h3>
                        {isSearching && <div className="text-xs text-gray-500">Searching...</div>}
                      </div>
                      {searchResults.length === 0 ? (
                        <div className="flex justify-center items-center h-20">
                          <div className="text-sm text-gray-500 text-center">
                            No messages found
                          </div>
                        </div>
                      ) : (
                        searchResults.map((message) => (
                          <div
                            key={message.id}
                            className="p-3 rounded-lg border bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors"
                            onClick={() => {
                              // Find the conversation for this message
                              const roomId = (message as any).room_id;
                              const roomName = (message as any).room_name;
                              const roomType = (message as any).room_type;
                              
                              // Try to find the conversation in our lists
                              let targetConversation = channels.find(c => c.id === roomId);
                              if (!targetConversation) {
                                targetConversation = groups.find(g => g.id === roomId);
                              }
                              if (!targetConversation) {
                                targetConversation = directMessages.find(dm => dm.id === roomId);
                              }
                              
                              if (targetConversation) {
                                handleConversationSelect(targetConversation);
                                setShowSearchResults(false);
                                setSearchQuery('');
                              }
                            }}
                          >
                            <div className="text-xs text-gray-500 mb-1">
                              {(message as any).room_name || 'Unknown'} • {formatMessageTime(message.timestamp)}
                            </div>
                            <div className="text-sm font-medium text-gray-700 mb-1">
                              {message.user?.name || message.user?.username || 'Unknown'}
                            </div>
                            <div className="text-sm text-gray-600 truncate">
                              {message.text || message.content}
                            </div>
                          </div>
                        ))
                      )}
                    </>
                  ) : filteredConversations.length === 0 ? (
                    <div className="flex justify-center items-center h-20">
                      <div className="text-sm text-gray-500 text-center">
                        No conversations found
                      </div>
                    </div>
                  ) : (
                    filteredConversations.map((conversation) => {
                      console.log('🎨 Rendering conversation:', {
                        id: conversation.id,
                        name: conversation.name,
                        type: conversation.type,
                        display_name: conversation.display_name,
                        other_user: conversation.other_user
                      });
                      
                      const isSelected = selectedConversation?.id === conversation.id;
                      console.log("Check the conversation type:", conversation.type);
                      const isDM = conversation.type === 'direct_message';
                      const isGroup = conversation.type === 'private_group';
                      const isChannel = conversation.type === 'channel';
                      
                      return (
                        <div
                          key={conversation.id}
                          className={`p-3 rounded-lg border hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors ${
                            isSelected ? 'bg-primary/10 border-primary' : ''
                          } ${isDM ? 'bg-green-50 border-green-200' : ''} ${isGroup ? 'bg-purple-50 border-purple-200' : ''}`}
                          onClick={() => handleConversationSelect(conversation)}
                          style={{
                            backgroundColor: isDM ? '#f0fdf4' : isGroup ? '#faf5ff' : undefined,
                            borderColor: isDM ? '#bbf7d0' : isGroup ? '#d8b4fe' : undefined,
                            borderWidth: (isDM || isGroup) ? '2px' : undefined
                          }}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <div className={`w-2 h-2 rounded-full ${
                                isDM ? 'bg-green-500' : isGroup ? 'bg-purple-500' : 'bg-blue-500'
                              }`}></div>
                              <div>
                                <div className="font-medium text-sm">
                                  {isDM ? conversation.other_user : (conversation.display_name || conversation.name || conversation.other_user)}
                                  {isDM && <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">DM</span>}
                                  {isGroup && <span className="ml-2 text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">Group</span>}
                                  {isChannel && <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Channel</span>}
                                </div>
                                {conversation.description && (
                                  <div className="text-xs text-gray-500 truncate">
                                    {conversation.description}
                                  </div>
                                )}
                              </div>
                            </div>
                            <div className="text-xs text-gray-400">
                              {conversation.unread_count && conversation.unread_count > 0 ? `${conversation.unread_count} msgs` : 'Click to view'}
                            </div>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </ScrollArea>
            </Card>
          </div>

          {/* Chat Window */}
          <div className="md:col-span-7 lg:col-span-8">
            {selectedConversation ? (
              <div className="h-full bg-card rounded-lg border flex flex-col">
                {/* Chat Header */}
                <div className="p-4 border-b flex-shrink-0">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xl ${
                        selectedConversation.type === 'direct_message' ? 'bg-green-500' :
                        selectedConversation.type === 'private_group' ? 'bg-purple-500' : 'bg-blue-500'
                      }`}>
                        {selectedConversation.type === 'direct_message' ? <User className="h-5 w-5" /> :
                         selectedConversation.type === 'private_group' ? <Users className="h-5 w-5" /> : <Hash className="h-5 w-5" />}
                      </div>
                      <div>
                        <h2 className="font-semibold">
                          {selectedConversation.type === 'direct_message' 
                            ? selectedConversation.name
                            : (selectedConversation.display_name || selectedConversation.name || selectedConversation.other_user)
                          }
                        </h2>
                        <p className="text-sm text-muted-foreground">
                          {selectedConversation.type === 'direct_message' ? selectedConversation.other_user :
                           selectedConversation.type === 'private_group' ? 'Private Group' : 'Rocket.Chat Channel'}
                        </p>
                      </div>
                    </div>
                    {/* Audio call button - only show for DMs */}
                    {selectedConversation.type === 'direct_message' && (
                      <button
                        onClick={() => {
                          toast({
                            title: "Audio Call",
                            description: "Initiating audio call with " + (selectedConversation.name || selectedConversation.other_user),
                          });
                          console.log('📞 Starting audio call with:', selectedConversation.name || selectedConversation.other_user);
                        }}
                        className="p-2 hover:bg-gray-200 rounded-full transition-colors flex items-center gap-2"
                        title="Start audio call"
                      >
                        <Phone className="h-5 w-5 text-blue-600" />
                      </button>
                    )}
                  </div>
                </div>

                {/* Pinned Messages Header */}
                {pinnedMessages.length > 0 && (
                  <div className="border-b bg-blue-50 p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Pin className="h-4 w-4 text-blue-600 fill-current" />
                      <span className="text-sm font-semibold text-blue-900">
                        Pinned Messages ({pinnedMessages.length})
                      </span>
                    </div>
                    <ScrollArea className="max-h-48 overflow-y-auto">
                      <div className="space-y-2 pr-4">
                        {pinnedMessages.map((pinnedMsg) => (
                          <div 
                            key={pinnedMsg.id}
                            className="bg-white rounded-md p-2 text-sm border border-blue-200"
                          >
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1 min-w-0">
                                <p className="text-gray-800 truncate">{pinnedMsg.text}</p>
                                <p className="text-xs text-gray-500 mt-1">
                                  Pinned {new Date(pinnedMsg.timestamp).toLocaleDateString()}
                                </p>
                              </div>
                              <button
                                onClick={async () => {
                                  try {
                                    // Build proper room_id for DMs
                                    const roomId = selectedConversation?.type === 'direct_message'
                                      ? `dm:${selectedConversation?.name || selectedConversation?.other_user || ''}`
                                      : selectedConversation?.id;
                                    
                                    const response = await fetch('http://localhost:8000/chat/unpin-message', {
                                      method: 'POST',
                                      headers: {
                                        'Content-Type': 'application/json',
                                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                                      },
                                      body: JSON.stringify({
                                        message_id: pinnedMsg.id,
                                        room_id: roomId
                                      })
                                    });
                                    
                                    const data = await response.json();
                                    
                                    if (response.ok && data.success) {
                                      toast({
                                        title: "Message unpinned!",
                                        description: data.message || "Message has been unpinned successfully",
                                      });
                                      
                                      // Immediately remove from pinned messages array
                                      setPinnedMessages(prev => prev.filter(msg => msg.id !== pinnedMsg.id));
                                      
                                      // Remove from pinned set
                                      setPinnedMessageIds(prev => {
                                        const newSet = new Set(prev);
                                        newSet.delete(pinnedMsg.id);
                                        return newSet;
                                      });
                                      
                                      // Reload pinned messages to sync with server
                                      const reloadRoomId = selectedConversation?.type === 'direct_message'
                                        ? `dm:${selectedConversation?.name || selectedConversation?.other_user || ''}`
                                        : (selectedConversation?.id || '');
                                      loadPinnedMessages(reloadRoomId);
                                    } else {
                                      throw new Error(data.message || 'Failed to unpin message');
                                    }
                                  } catch (error) {
                                    console.error('Failed to unpin:', error);
                                    toast({
                                      title: "Error",
                                      description: error instanceof Error ? error.message : "Failed to unpin message",
                                      variant: "destructive",
                                    });
                                  }
                                }}
                                className="text-gray-400 hover:text-red-600 transition-colors flex-shrink-0"
                                title="Unpin message"
                              >
                                <Pin className="h-4 w-4 fill-current" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </div>
                )}

                {/* Messages Area */}
                <ScrollArea className="flex-1 overflow-y-auto p-4 scrollbar-hide min-h-0 max-h-full">
                  <div className="space-y-4 pb-4">
                    {loadingMessages ? (
                      <div className="text-center text-muted-foreground py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                        <p>Loading messages...</p>
                      </div>
                    ) : messages.length === 0 ? (
                      <div className="text-center text-muted-foreground py-8">
                        <div className="text-6xl mb-4">💬</div>
                        <p>No messages yet. Start a conversation!</p>
                      </div>
                    ) : (
                      (() => {
                        const messageElements: React.ReactNode[] = [];
                        let lastDate: string | null = null;
                        
                        messages.forEach((message, index) => {
                          // Use the same comprehensive thread detection
                          const isThread = (msg: any): boolean => {
                            console.log('🔍 Rendering-level thread detection for message:', {
                              id: msg.id,
                              text: msg.text,
                              content: msg.content,
                              sender: msg.sender,
                              is_thread_message: msg.is_thread_message,
                              thread_ts: msg.thread_ts,
                              tmid: msg.tmid,
                              timestamp: msg.timestamp
                            });
                            
                            // Only check for explicit thread metadata - no heuristics
                            if (msg.is_thread_message === true) {
                              console.log('✅ Rendering: Thread message detected (explicit flag)');
                              return true;
                            }
                            if (msg.thread_ts || msg.tmid) {
                              console.log('✅ Rendering: Thread message detected (thread metadata)');
                              return true;
                            }
                            
                            console.log('❌ Rendering: Message NOT detected as thread message');
                            return false;
                          };
                          
                          if (isThread(message)) {
                            console.log('🚫 Skipping thread message in rendering:', message.id, message.text, message.sender);
                            return;
                          }
                          
                          
                          const currentMessageDate = new Date(message.timestamp).toDateString();
                          const showDateSeparator = currentMessageDate !== lastDate;
                          
                          if (showDateSeparator) {
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
                          
                          const isSystemMessage = message.type === 'system';
                          
                          // Debug system messages
                          if (isSystemMessage) {
                            console.log('🔄 System message detected:', {
                              id: message.id,
                              type: message.type,
                              text: message.text,
                              content: message.content,
                              sender: message.sender,
                              user: message.user
                            });
                          }
                          
                          // Determine if this message is from the current user
                          const currentUserUsername = user?.email?.split('@')[0]; // e.g., 'ankush8'
                          const currentUserName = user?.name?.toLowerCase().replace(/\s+/g, ''); // e.g., 'ankushchhabra'
                          const currentUserFullName = user?.name; // e.g., 'Ankush Chhabra'
                          
                          // Simple: Use the isOwn flag from backend (it's already calculated correctly)
                          const isOwnMessage = message.isOwn === true;
                          
                          console.log('🔍 Message ownership check:', {
                            messageId: message.id,
                            messageSender: message.sender,
                            messageUser: message.user?.username,
                            messageUserName: message.user?.name,
                            currentUserUsername,
                            currentUserName,
                            currentUserEmail: user?.email,
                            currentUserFullName: user?.name,
                            isOwnMessage,
                            messageData: message,
                            // Additional checks
                            senderMatchesUsername: message.sender === currentUserUsername,
                            senderMatchesName: message.sender === currentUserName,
                            senderMatchesFullName: message.sender === currentUserFullName,
                            senderMatchesUser: message.sender === user?.name
                          });
                          
                          messageElements.push(
                            <div key={message.id} className={`${message.is_thread_message ? 'ml-6 border-l-2 border-muted pl-4' : ''}`}>
                              <div className={`flex ${isOwnMessage && !isSystemMessage ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                                  isSystemMessage
                                    ? 'bg-muted text-center text-sm italic mx-auto'
                                    : isOwnMessage
                                    ? 'bg-primary text-primary-foreground ml-auto'
                                    : 'bg-muted mr-auto'
                                }`}>
                                  {!isSystemMessage && !isOwnMessage && (
                                    <div className="text-xs text-muted-foreground mb-1">
                                      {message.user?.username || message.user?.name || message.sender}
                                    </div>
                                  )}
                                  
                                  {/* Check if this is a forwarded message */}
                                  {message.attachments && message.attachments.length > 0 && message.attachments[0]?.type === 'forwarded_message' ? (
                                    <div className="border-l-2 border-gray-400 pl-3 py-2">
                                      <div className="text-xs font-semibold text-gray-600 mb-1">
                                        {message.attachments[0].author_name}
                                      </div>
                                      <p className="text-sm">{message.attachments[0].text}</p>
                                    </div>
                                  ) : (
                                    <div className="text-sm">{renderMessageContent(message.text || message.content)}</div>
                                  )}
                                  
                                  {/* File Attachments Display */}
                                  {message.attachments && message.attachments.length > 0 && (
                                    <div className="mt-2 space-y-2">
                                      {message.attachments.map((attachment: any, index: number) => {
                                        // Skip forwarded messages - they're already displayed above
                                        if (attachment.type === 'forwarded_message') {
                                          return null;
                                        }
                                        
                                        // Check if attachment is an image
                                        const isImage = attachment.type && attachment.type.startsWith('image/');
                                        const isImageFile = attachment.filename && 
                                          /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i.test(attachment.filename);
                                        
                                        // For images, show full size
                                        if (isImage || isImageFile) {
                                          // Use base64 preview for instant display (it's full quality)

                                          const imageUrl = attachment.url;
                                          
                                          console.log("This is the image URL being used:", imageUrl);
                                          
                                          console.log('🎨 Rendering image attachment:', {
                                            filename: attachment.filename,
                                            type: attachment.type,
                                            hasPreview: !!attachment.preview,
                                            hasUrl: !!attachment.url,
                                            usingPreview: !!attachment.preview
                                          });
                                          
                                          return (
                                            <div key={index} className="relative group">
                                              {imageUrl && (
                                                <>
                                                  <img 
                                                    src={imageUrl} 
                                                    alt={attachment.title || attachment.filename || 'Image'} 
                                                    className="rounded-lg border border-gray-200"
                                                    style={{ maxHeight: '415px', maxWidth: '415px', width: 'auto', height: 'auto' }}
                                                    onError={(e) => {
                                                      console.error('❌ Image failed to load:', imageUrl);
                                                      // Try the other URL if one fails
                                                      if (attachment.url && imageUrl === attachment.preview) {
                                                        console.log('🔄 Trying full URL as fallback');
                                                        (e.target as HTMLImageElement).src = attachment.url;
                                                      } else if (attachment.preview && imageUrl === attachment.url) {
                                                        console.log('🔄 Trying preview as fallback');
                                                        (e.target as HTMLImageElement).src = attachment.preview;
                                                      }
                                                    }}
                                                    onLoad={() => {
                                                      console.log('✅ Image loaded successfully');
                                                    }}
                                                  />
                                                  
                                                  {/* Download button */}
                                                  <button
                                                    onClick={(e) => {
                                                      e.stopPropagation();
                                                      const link = document.createElement('a');
                                                      link.href = imageUrl;
                                                      link.download = attachment.filename || attachment.title || 'image.jpg';
                                                      link.target = '_blank';
                                                      document.body.appendChild(link);
                                                      link.click();
                                                      document.body.removeChild(link);
                                                    }}
                                                    className="absolute top-2 right-2 bg-gray-800 hover:bg-gray-900 text-white p-2 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
                                                    title="Download image"
                                                  >
                                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                                    </svg>
                                                  </button>
                                                </>
                                              )}
                                            </div>
                                          );
                                        }
                                        
                                        // For non-image files, show file info with download button
                                        return (
                                          <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg border">
                                            <File className="h-4 w-4 text-blue-600" />
                                            <div className="flex-1 min-w-0">
                                              <p className="text-sm font-medium text-gray-900 truncate">
                                                {attachment.title || attachment.filename || 'File'}
                                              </p>
                                              <p className="text-xs text-gray-500">
                                                {attachment.size ? `${(attachment.size / 1024).toFixed(1)} KB` : 'Unknown size'}
                                              </p>
                                            </div>
                                            <Button
                                              variant="ghost"
                                              size="sm"
                                              onClick={() => window.open(attachment.url, '_blank')}
                                              className="text-blue-600 hover:text-blue-800"
                                            >
                                              Download
                                            </Button>
                                          </div>
                                        );
                                      })}
                                    </div>
                                  )}
                                  
                                  <div className="text-xs opacity-70 mt-1 flex items-center gap-1">
                                    {formatMessageTime(message.timestamp)}
                                    {message.editedAt && <span className="text-gray-500 italic">edited</span>}
                                  </div>
                                  
                                  {/* Reactions Display */}
                                  {message.reactions && Object.keys(message.reactions).length > 0 && (
                                    <div className="flex flex-wrap gap-1 mt-2">
                                      {Object.entries(message.reactions).map(([emoji, usernames]) => {
                                        // Only show reactions that have users
                                        if (!usernames || usernames.length === 0) return null;
                                        return (
                                          <button
                                            key={emoji}
                                            className="flex items-center space-x-1 px-2 py-1 rounded-full bg-secondary/50 hover:bg-secondary text-xs"
                                            onClick={() => handleReactionToggle(message.id, emoji)}
                                          >
                                            <span>{emoji}</span>
                                            <span>{usernames.length}</span>
                                          </button>
                                        );
                                      })}
                                    </div>
                                  )}
                                  
                                  {/* Add Reaction Button */}
                                  {!isSystemMessage && (
                                    <div className="flex items-center space-x-2 mt-2">
                                      <div className="relative">
                                        <button
                                          onClick={() => setShowReactionPicker(showReactionPicker === message.id ? null : message.id)}
                                          className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors"
                                          title="Add reactions"
                                        >
                                          <Smile className="h-4 w-4" />
                                        </button>
                                        
                                        {/* Enhanced Reaction Picker */}
                                        {showReactionPicker === message.id && (
                                          <div className="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-3 z-10 min-w-[200px]">
                                            <div className="text-xs font-medium text-gray-600 mb-2">Quick Reactions</div>
                                            <div className="grid grid-cols-4 gap-1 mb-2">
                                              {['👍', '❤️', '😂', '😮', '😢', '😡', '🔥', '💯', '🎉', '👏', '🤔', '😍'].map((emoji) => (
                                                <button
                                                  key={emoji}
                                                  className="text-lg hover:bg-gray-100 rounded p-2 transition-colors flex items-center justify-center"
                                                  onClick={() => {
                                                    handleReactionToggle(message.id, emoji);
                                                    setShowReactionPicker(null);
                                                  }}
                                                  title={`React with ${emoji}`}
                                                >
                                                  {emoji}
                                                </button>
                                              ))}
                                            </div>
                                            <div className="text-xs text-gray-500 text-center">
                                              Click to add or remove reaction
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                      
                                      {/* Thread Reply Button */}
                                      <div className="relative">
                                        <button
                                          onClick={() => {
                                            if (openThreads.has(message.id)) {
                                              setOpenThreads(prev => {
                                                const newSet = new Set(prev);
                                                newSet.delete(message.id);
                                                return newSet;
                                              });
                                            } else {
                                              setOpenThreads(prev => new Set(prev).add(message.id));
                                              handleLoadThread(message.id);
                                            }
                                          }}
                                          className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors relative"
                                          title="Reply in thread"
                                        >
                                          <Reply className="h-4 w-4" />
                                          {/* Thread count badge */}
                                          {(message.thread_count && message.thread_count > 0) && (
                                            <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-[10px] font-bold rounded-full min-w-[16px] h-4 px-1 flex items-center justify-center">
                                              {message.thread_count}
                                            </span>
                                          )}
                                        </button>
                                        
                                        {/* Pin/Unpin button */}
                                        <button
                                          onClick={async () => {
                                            const isCurrentlyPinned = pinnedMessageIds.has(message.id);
                                            
                                            try {
                                              // Determine room_id based on conversation type
                                              let roomId = '';
                                              let roomName = '';
                                              let roomType = '';
                                              
                                              if (selectedConversation?.type === 'direct_message') {
                                                // For DMs, use a composite ID based on username
                                                const dmUsername = selectedConversation?.name || selectedConversation?.other_user || '';
                                                roomId = `dm:${dmUsername}`;
                                                roomName = selectedConversation?.display_name || selectedConversation?.name || selectedConversation?.other_user || dmUsername || 'DM';
                                                roomType = 'direct_message';
                                              } else if (selectedConversation?.type === 'private_group') {
                                                // For private groups, prefer rocket_chat_group_id
                                                roomId = (selectedConversation as any).rocket_chat_group_id || selectedConversation?.id || '';
                                                
                                                // Fallback to finding rocket_chat_group_id from groups
                                                if (!roomId || !roomId.startsWith('6')) {
                                                  const group = groups.find(g => g.id === selectedConversation.id || g.name === selectedConversation.name);
                                                  if (group && (group as any).rocket_chat_group_id) {
                                                    roomId = (group as any).rocket_chat_group_id;
                                                  }
                                                }
                                                
                                                roomName = selectedConversation?.name || selectedConversation?.display_name || '';
                                                roomType = 'private_group';
                                              } else {
                                                // For channels, use the ID
                                                roomId = selectedConversation?.id || '';
                                                roomName = selectedConversation?.name || selectedConversation?.display_name || '';
                                                roomType = 'channel';
                                              }
                                              
                                              if (isCurrentlyPinned) {
                                                // Unpin the message
                                                console.log('📌 Unpinning message:', { messageId: message.id, roomId, roomType });
                                                
                                                const response = await fetch('http://localhost:8000/chat/unpin-message', {
                                                  method: 'POST',
                                                  headers: {
                                                    'Content-Type': 'application/json',
                                                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                                                  },
                                                  body: JSON.stringify({
                                                    message_id: message.id,
                                                    room_id: roomId,
                                                    room_name: roomName,
                                                    room_type: roomType
                                                  })
                                                });
                                                
                                                const data = await response.json();
                                                
                                                if (!response.ok || !data.success) {
                                                  throw new Error(data.message || 'Failed to unpin message');
                                                }
                                                
                                                toast({
                                                  title: "Message unpinned!",
                                                  description: data.message || "The message has been unpinned successfully",
                                                });
                                                
                                                // Remove from pinned messages set
                                                setPinnedMessageIds(prev => {
                                                  const newSet = new Set(prev);
                                                  newSet.delete(message.id);
                                                  return newSet;
                                                });
                                                
                                                // Reload pinned messages to update the header
                                                // For DMs, pass the proper room_id format
                                                const reloadRoomId = selectedConversation?.type === 'direct_message' 
                                                  ? `dm:${selectedConversation?.name || selectedConversation?.other_user || ''}`
                                                  : roomId;
                                                loadPinnedMessages(reloadRoomId);
                                              } else {
                                                // Pin the message
                                                console.log('📌 Pinning message:', { messageId: message.id, roomId, roomName, roomType });
                                                
                                                const response = await fetch('http://localhost:8000/chat/pin-message', {
                                                  method: 'POST',
                                                  headers: {
                                                    'Content-Type': 'application/json',
                                                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                                                  },
                                                  body: JSON.stringify({
                                                    message_id: message.id,
                                                    room_id: roomId,
                                                    room_name: roomName,
                                                    room_type: roomType,
                                                    message_text: message.text || message.content || ''
                                                  })
                                                });
                                                
                                                const data = await response.json();
                                                
                                                if (!response.ok || !data.success) {
                                                  throw new Error(data.message || 'Failed to pin message');
                                                }
                                                
                                                toast({
                                                  title: "Message pinned!",
                                                  description: data.message || "The message has been pinned successfully",
                                                });
                                                
                                                // Add to pinned messages set
                                                setPinnedMessageIds(prev => new Set(prev).add(message.id));
                                                
                                                // Reload pinned messages with proper room_id format for DMs
                                                if (selectedConversation) {
                                                  const reloadRoomId = selectedConversation.type === 'direct_message'
                                                    ? `dm:${selectedConversation.name || selectedConversation.other_user || ''}`
                                                    : selectedConversation.id;
                                                  loadPinnedMessages(reloadRoomId);
                                                }
                                              }
                                            } catch (error) {
                                              console.error(`Failed to ${isCurrentlyPinned ? 'unpin' : 'pin'} message:`, error);
                                              toast({
                                                title: "Error",
                                                description: error instanceof Error ? error.message : `Failed to ${isCurrentlyPinned ? 'unpin' : 'pin'} message`,
                                                variant: "destructive",
                                              });
                                            }
                                          }}
                                          className={`flex items-center justify-center w-6 h-6 rounded-full transition-colors ${
                                            pinnedMessageIds.has(message.id)
                                              ? 'bg-blue-100 hover:bg-blue-200 text-blue-600'
                                              : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                                          }`}
                                          title={pinnedMessageIds.has(message.id) ? "Click to unpin message" : "Click to pin message"}
                                        >
                                          <Pin className={`h-4 w-4 ${pinnedMessageIds.has(message.id) ? 'fill-current' : ''}`} />
                                        </button>
                                        
                                        {/* Forward button */}
                                        <button
                                          onClick={async () => {
                                            setForwardingMessageId(message.id);
                                            setShowForwardDialog(true);
                                            setForwardSearchQuery('');
                                            setForwardSearchResults([]);
                                            setForwardingTo(null);
                                            
                                            // Load forward targets from backend
                                            try {
                                              const response = await fetch('http://localhost:8000/chat/forward-targets', {
                                                headers: {
                                                  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                                                }
                                              });
                                              
                                              if (!response.ok) {
                                                throw new Error('Failed to load forward targets');
                                              }
                                              
                                              const data = await response.json();
                                              console.log('Forward targets loaded:', data);
                                              setChannels(data.channels || []);
                                              setGroups(data.groups || []);
                                              setDirectMessages(data.direct_messages || []);
                                            } catch (error) {
                                              console.error('Error loading forward targets:', error);
                                              toast({
                                                title: "Error",
                                                description: "Failed to load conversations",
                                                variant: "destructive"
                                              });
                                            }
                                          }}
                                          className="flex items-center justify-center w-6 h-6 rounded-full transition-colors bg-gray-100 hover:bg-gray-200 text-gray-600"
                                          title="Forward message"
                                        >
                                          <Share2 className="h-4 w-4" />
                                        </button>
                                        
                                        {/* Edit button (only show for own messages) */}
                                        {isOwnMessage && !isSystemMessage && (
                                          <button
                                            onClick={() => {
                                              setEditingMessageId(message.id);
                                              setEditingMessageText(message.text || message.content || '');
                                              setShowEditDialog(true);
                                            }}
                                            className="flex items-center justify-center w-6 h-6 rounded-full transition-colors bg-gray-100 hover:bg-gray-200 text-gray-600"
                                            title="Edit message"
                                          >
                                            <Edit className="h-4 w-4" />
                                          </button>
                                        )}
                                        
                                        {/* Delete button */}
                                        <button
                                          onClick={async () => {
                                              if (!confirm('Are you sure you want to delete this message? This action cannot be undone.')) {
                                                return;
                                              }
                                              
                                              try {
                                                // Prepare delete request body
                                                const deleteBody: any = {
                                                  message_id: message.id,
                                                };
                                                
                                                // Check if this is a forwarded message
                                                const storedRoomId = localStorage.getItem(`fwd_msg_room_${message.id}`);
                                                
                                                if (storedRoomId) {
                                                  // This is a forwarded message, use the stored room ID
                                                  deleteBody.room_id = storedRoomId;
                                                  console.log('🗑️ Deleting forwarded message from room:', storedRoomId);
                                                } else if (selectedConversation?.type === 'direct_message') {
                                                  // For DMs, add username instead of room_id
                                                  const dmUsername = selectedConversation?.name || selectedConversation?.other_user || '';
                                                  deleteBody.username = dmUsername;
                                                  console.log('🗑️ Deleting DM message from conversation with:', dmUsername);
                                                } else {
                                                  // For channels/groups, use room_id
                                                  let roomId = selectedConversation?.id || '';
                                                  
                                                  // For private groups, prefer rocket_chat_group_id
                                                  if (selectedConversation?.type === 'private_group') {
                                                    const group = groups.find(g => g.id === selectedConversation.id || g.name === selectedConversation.name);
                                                    if (group && (group as any).rocket_chat_group_id) {
                                                      roomId = (group as any).rocket_chat_group_id;
                                                    } else if ((selectedConversation as any).rocket_chat_group_id) {
                                                      roomId = (selectedConversation as any).rocket_chat_group_id;
                                                    }
                                                  }
                                                  
                                                  deleteBody.room_id = roomId;
                                                  console.log('🗑️ Deleting channel/group message from room:', roomId);
                                                }
                                                
                                                console.log('📤 Delete request body:', deleteBody);
                                                
                                                const response = await fetch('http://localhost:8000/chat/delete-message', {
                                                  method: 'DELETE',
                                                  headers: {
                                                    'Content-Type': 'application/json',
                                                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                                                  },
                                                  body: JSON.stringify(deleteBody)
                                                });
                                                
                                                const data = await response.json();
                                                
                                                if (!response.ok || !data.success) {
                                                  throw new Error(data.message || data.detail || 'Failed to delete message');
                                                }
                                                
                                                toast({
                                                  title: "Message deleted!",
                                                  description: "The message has been deleted successfully",
                                                });
                                                
                                                // Remove from messages array
                                                setMessages(prev => prev.filter(msg => msg.id !== message.id));
                                                
                                                // Remove from pinned messages if it was pinned
                                                if (pinnedMessageIds.has(message.id)) {
                                                  setPinnedMessageIds(prev => {
                                                    const newSet = new Set(prev);
                                                    newSet.delete(message.id);
                                                    return newSet;
                                                  });
                                                  
                                                  // Remove from pinned messages array
                                                  setPinnedMessages(prev => prev.filter(msg => msg.id !== message.id));
                                                  
                                                  // Reload pinned messages with proper room_id format for DMs
                                                  if (selectedConversation) {
                                                    const reloadRoomId = selectedConversation.type === 'direct_message'
                                                      ? `dm:${selectedConversation.name || selectedConversation.other_user || ''}`
                                                      : selectedConversation.id;
                                                    loadPinnedMessages(reloadRoomId);
                                                  }
                                                }
                                              } catch (error) {
                                                console.error('Failed to delete message:', error);
                                                
                                                // Parse error message to provide user-friendly feedback
                                                let errorMessage = "Failed to delete message";
                                                
                                                if (error instanceof Error) {
                                                  const errorText = error.message.toLowerCase();
                                                  
                                                  // Check for common error scenarios
                                                  if (errorText.includes('not allowed') || errorText.includes('error-action-not-allowed')) {
                                                    errorMessage = "Cannot delete other users' messages. You can only delete your own messages.";
                                                  } else if (errorText.includes('not authorized') || errorText.includes('unauthorized')) {
                                                    errorMessage = "You don't have permission to delete this message.";
                                                  } else if (errorText.includes('not found')) {
                                                    errorMessage = "Message not found or already deleted.";
                                                  } else {
                                                    errorMessage = error.message;
                                                  }
                                                }
                                                
                                                toast({
                                                  title: "Cannot Delete Message",
                                                  description: errorMessage,
                                                  variant: "destructive",
                                                });
                                              }
                                            }}
                                            className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 hover:bg-red-100 text-gray-600 hover:text-red-600 transition-colors"
                                            title="Delete message"
                                          >
                                            <Trash2 className="h-4 w-4" />
                                          </button>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                              
                              {/* Thread messages - Display only when thread is opened */}
                              {openThreads.has(message.id) ? (
                                <div className="mt-2 space-y-2">
                                  {/* Show loading state while fetching */}
                                  {loadingThread === message.id && !threadMessages[message.id] && (!message.thread_messages || message.thread_messages.length === 0) && (
                                    <div className="ml-6 pl-4 py-2 text-sm text-muted-foreground">
                                      Loading thread...
                                    </div>
                                  )}
                                  
                                  {/* Show thread messages - merge fetched data with initial backend response */}
                                  {(() => {
                                    // Combine messages from both sources, avoiding duplicates
                                    const fetchedMsgs = threadMessages[message.id] || [];
                                    const initialMsgs = message.thread_messages || [];
                                    
                                    console.log('🧵 Thread message rendering:', {
                                      messageId: message.id,
                                      fetchedCount: fetchedMsgs.length,
                                      initialCount: initialMsgs.length,
                                      fetchedMsgs: fetchedMsgs,
                                      initialMsgs: initialMsgs,
                                      messageHasThreadMessages: !!message.thread_messages,
                                      threadMessagesLength: message.thread_messages?.length
                                    });
                                    const seenIds = new Set<string>();
                                    const allMsgs = [...fetchedMsgs, ...initialMsgs].filter(msg => {
                                      if (seenIds.has(msg.id)) return false;
                                      seenIds.add(msg.id);
                                      return true;
                                    });
                                    
                                    // Sort by timestamp (oldest first)
                                    allMsgs.sort((a, b) => {
                                      const timeA = new Date(a.timestamp).getTime();
                                      const timeB = new Date(b.timestamp).getTime();
                                      return timeA - timeB;
                                    });
                                    
                                    return allMsgs.map((threadMsg) => {
                                    // Check isOwn flag from backend (it's already calculated correctly)
                                    const isOwnThreadMessage = threadMsg.isOwn === true;
                                    
                                    console.log(`🔍 Thread message ${threadMsg.id}: isOwn=${threadMsg.isOwn}, isOwnThreadMessage=${isOwnThreadMessage}`, threadMsg);
                                    
                                    return (
                                      <div key={threadMsg.id} className="ml-6 border-l-2 border-muted pl-4 group flex gap-2 items-center">
                                        <div className={`flex-1 ${isOwnThreadMessage ? 'flex justify-end' : 'flex justify-start'}`}>
                                          <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                                            isOwnThreadMessage
                                              ? 'bg-primary text-primary-foreground'
                                              : 'bg-muted/50'
                                          }`}>
                                            {!isOwnThreadMessage && (
                                              <div className="text-xs text-muted-foreground mb-1">
                                                {threadMsg.user?.username || threadMsg.user?.name}
                                              </div>
                                            )}
                                            
                                            {/* Check if this is a forwarded message */}
                                            {threadMsg.attachments && threadMsg.attachments.length > 0 && threadMsg.attachments[0]?.type === 'forwarded_message' ? (
                                              <div className="border-l-2 border-gray-400 pl-3 py-2">
                                                <div className="text-xs font-semibold opacity-75 mb-1">
                                                  {threadMsg.attachments[0].author_name}
                                                </div>
                                                <p className="text-sm">{threadMsg.attachments[0].text}</p>
                                              </div>
                                            ) : (
                                              <div className="text-sm">{renderMessageContent(threadMsg.text || threadMsg.content)}</div>
                                            )}
                                            
                                            <div className="text-xs opacity-70 mt-1 flex items-center gap-1">
                                              {formatMessageTime(threadMsg.timestamp)}
                                              {threadMsg.editedAt && <span className="text-gray-500 italic">edited</span>}
                                            </div>
                                            
                                            {/* Reactions Display for thread messages */}
                                            {threadMsg.reactions && Object.keys(threadMsg.reactions).length > 0 && (
                                              <div className="flex flex-wrap gap-1 mt-2">
                                                {Object.entries(threadMsg.reactions).map(([emoji, usernames]) => {
                                                  if (!usernames || usernames.length === 0) return null;
                                                  return (
                                                    <button
                                                      key={emoji}
                                                      className="flex items-center space-x-1 px-2 py-1 rounded-full bg-secondary/50 hover:bg-secondary text-xs"
                                                      onClick={() => handleReactionToggle(threadMsg.id, emoji)}
                                                    >
                                                      <span>{emoji}</span>
                                                      <span>{usernames.length}</span>
                                                    </button>
                                                  );
                                                })}
                                              </div>
                                            )}
                                            
                                            {/* Add Reaction Button for thread messages */}
                                            <div className="flex items-center space-x-2 mt-2">
                                              <div className="relative">
                                                <button
                                                  onClick={() => setShowReactionPicker(showReactionPicker === threadMsg.id ? null : threadMsg.id)}
                                                  className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors"
                                                  title="Add reactions"
                                                >
                                                  <Smile className="h-4 w-4" />
                                                </button>
                                                
                                                {showReactionPicker === threadMsg.id && (
                                                  <div className="absolute bottom-full mb-2 left-0 bg-white border rounded-lg shadow-lg p-2 z-50" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.5rem' }}>
                                                    {['👍', '❤️', '😂', '😮', '😢', '😡', '🎉', '👏', '🤔', '😍'].map((emoji) => (
                                                      <button
                                                        key={emoji}
                                                        onClick={async () => {
                                                          await handleReactionToggle(threadMsg.id, emoji);
                                                          setShowReactionPicker(null);
                                                        }}
                                                        className="text-xl hover:scale-125 transition-transform"
                                                      >
                                                        {emoji}
                                                      </button>
                                                    ))}
                                                  </div>
                                                )}
                                              </div>
                                            </div>
                                          </div>
                                        </div>
                                        
                                        {/* Thread message action buttons - show on hover */}
                                        {isOwnThreadMessage && (
                                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 group-hover:pointer-events-auto pointer-events-none transition-opacity flex-shrink-0">
                                              {/* Edit button - only for own messages */}
                                              <button
                                                onClick={() => {
                                                  setEditingMessageId(threadMsg.id);
                                                  setEditingMessageText(threadMsg.text || threadMsg.content || '');
                                                  setShowEditDialog(true);
                                                }}
                                                className="flex items-center justify-center w-6 h-6 rounded-full transition-colors bg-gray-100 hover:bg-gray-200 text-gray-600"
                                                title="Edit message"
                                              >
                                                <Edit className="h-4 w-4" />
                                              </button>
                                              
                                              {/* Delete button - only for own messages */}
                                              <button
                                                onClick={async () => {
                                                  if (!confirm('Are you sure you want to delete this thread message? This action cannot be undone.')) {
                                                    return;
                                                  }
                                                  
                                                  try {
                                                    const deleteBody: any = {
                                                      message_id: threadMsg.id,
                                                    };
                                                    
                                                    if (selectedConversation?.type === 'direct_message') {
                                                      const dmUsername = selectedConversation?.name || selectedConversation?.other_user || '';
                                                      deleteBody.username = dmUsername;
                                                    } else {
                                                      // For channels/groups, use room_id
                                                      let roomId = selectedConversation?.id || '';
                                                      
                                                      // For private groups, prefer rocket_chat_group_id
                                                      if (selectedConversation?.type === 'private_group') {
                                                        const group = groups.find(g => g.id === selectedConversation.id || g.name === selectedConversation.name);
                                                        if (group && (group as any).rocket_chat_group_id) {
                                                          roomId = (group as any).rocket_chat_group_id;
                                                        } else if ((selectedConversation as any).rocket_chat_group_id) {
                                                          roomId = (selectedConversation as any).rocket_chat_group_id;
                                                        }
                                                      }
                                                      
                                                      deleteBody.room_id = roomId;
                                                    }
                                                    
                                                    console.log('Deleting thread message:', deleteBody);
                                                    
                                                    const response = await fetch('http://localhost:8000/chat/delete-message', {
                                                      method: 'DELETE',
                                                      headers: {
                                                        'Content-Type': 'application/json',
                                                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                                                      },
                                                      body: JSON.stringify(deleteBody)
                                                    });
                                                    
                                                    console.log('Delete response status:', response.status);
                                                    const data = await response.json();
                                                    console.log('Delete response data:', data);
                                                    
                                                    if (response.ok && data.success) {
                                                      toast({
                                                        title: "Message deleted",
                                                        description: data.message || "Message has been deleted successfully",
                                                      });
                                                      
                                                      // Remove from messages state
                                                      setMessages(prevMessages =>
                                                        prevMessages.map(msg => ({
                                                          ...msg,
                                                          thread_messages: (msg.thread_messages || []).filter(tm => tm.id !== threadMsg.id)
                                                        }))
                                                      );
                                                      
                                                      // Also remove from threadMessages state if the thread is fetched
                                                      const parentMsg = messages.find(m => m.thread_messages?.some(tm => tm.id === threadMsg.id));
                                                      if (parentMsg && threadMessages[parentMsg.id]) {
                                                        setThreadMessages(prev => ({
                                                          ...prev,
                                                          [parentMsg.id]: prev[parentMsg.id].filter(msg => msg.id !== threadMsg.id)
                                                        }));
                                                      }
                                                    } else {
                                                      throw new Error(data.message || 'Failed to delete message');
                                                    }
                                                  } catch (error) {
                                                    console.error('Failed to delete message:', error);
                                                    toast({
                                                      title: "Error",
                                                      description: error instanceof Error ? error.message : "Failed to delete message",
                                                      variant: "destructive",
                                                    });
                                                  }
                                                }}
                                                className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 hover:bg-red-100 text-gray-600 hover:text-red-600 transition-colors"
                                                title="Delete message"
                                              >
                                                <Trash2 className="h-4 w-4" />
                                              </button>
                                            </div>
                                          )}
                                      </div>
                                    );
                                    });
                                  })()}

                                  {/* Thread reply input */}
                                  <div className="ml-6 pl-4">
                                    <div className="flex items-center space-x-2">
                                      <Input
                                        placeholder="Reply in thread..."
                                        value={threadReplyText[message.id] || ''}
                                        onChange={(e) => setThreadReplyText(prev => ({ ...prev, [message.id]: e.target.value }))}
                                        className="flex-1 text-sm"
                                        onKeyDown={(e) => {
                                          if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            e.stopPropagation();
                                            handleSendThreadReply(message.id);
                                          }
                                        }}
                                      />
                                      <Button
                                        size="sm"
                                        onClick={(e) => {
                                          e.preventDefault();
                                          e.stopPropagation();
                                          handleSendThreadReply(message.id);
                                        }}
                                        disabled={!threadReplyText[message.id]?.trim() || sendingThreadReply === message.id}
                                      >
                                        {sendingThreadReply === message.id ? 'Sending...' : 'Reply'}
                                      </Button>
                                    </div>
                                  </div>
                                </div>
                              ) : null}
                            </div>
                          );
                        });
                        
                        return messageElements;
                      })()
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                </ScrollArea>

                {/* Typing Indicators */}
                {selectedConversation && typingUsers[selectedConversation.id] && typingUsers[selectedConversation.id].length > 0 && (
                  <div className="px-4 py-2 bg-blue-50 border-t">
                    <div className="flex items-center space-x-2 text-sm text-blue-600">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span>
                        {typingUsers[selectedConversation.id].length === 1 
                          ? `${typingUsers[selectedConversation.id][0]} is typing...`
                          : `${typingUsers[selectedConversation.id].length} people are typing...`
                        }
                      </span>
                    </div>
                  </div>
                )}

                {/* Message Input */}
                <div className="p-4 border-t flex-shrink-0">
                  {/* File Upload Area */}
                  {selectedFiles.length > 0 && (
                    <div className="mb-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-blue-800">Selected Files:</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedFiles([])}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          Clear All
                        </Button>
                      </div>
                      <div className="space-y-2">
                        {selectedFiles.map((file, index) => (
                          <div key={index} className="flex items-center justify-between bg-white p-2 rounded border">
                            <div className="flex items-center space-x-2">
                              <File className="h-4 w-4 text-blue-600" />
                              <span className="text-sm text-gray-700">{file.name}</span>
                              <span className="text-xs text-gray-500">({(file.size / 1024).toFixed(1)} KB)</span>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setSelectedFiles(prev => prev.filter((_, i) => i !== index))}
                              className="text-red-600 hover:text-red-800"
                            >
                              Remove
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center space-x-2">
                    {/* File Upload Button */}
                    <div className="relative">
                      <input
                        type="file"
                        multiple
                        accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt"
                        onChange={handleFileSelect}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        id="file-upload"
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        className="cursor-pointer"
                        asChild
                      >
                        <label htmlFor="file-upload" className="cursor-pointer">
                          <Paperclip className="h-4 w-4" />
                        </label>
                      </Button>
                    </div>

                    {/* Message Input */}
                    <div className="flex-1 relative">
                      <Input
                        placeholder={`Message ${
                          selectedConversation.type === 'direct_message' 
                            ? selectedConversation.name
                            : (selectedConversation.display_name || selectedConversation.name || selectedConversation.other_user)
                        }...`}
                        value={newMessage}
                        onChange={(e) => {
                          setNewMessage(e.target.value);
                          if (e.target.value.length > 0) {
                            handleTypingStart();
                          } else {
                            handleTypingStop();
                          }
                        }}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleTypingStop();
                            handleSendMessage();
                          }
                        }}
                        onBlur={handleTypingStop}
                        className="w-full"
                      />
                    </div>

                    {/* Send Button */}
                    <Button 
                      onClick={handleSendMessage}
                      disabled={(!newMessage.trim() && selectedFiles.length === 0) || sendingMessage}
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center bg-card rounded-lg border">
                <div className="text-center text-muted-foreground">
                  {!isInitialized ? (
                    <>
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                      <h3 className="text-xl font-semibold mb-2">Loading Messages...</h3>
                      <p>Restoring your previous conversation...</p>
                    </>
                  ) : (
                    <>
                      <div className="text-6xl mb-4">💬</div>
                      <h3 className="text-xl font-semibold mb-2">Select a Conversation</h3>
                      <p>Choose a conversation from the sidebar to start viewing messages.</p>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* User Search Modal */}
      {showUserSearch && (
        <UserSearch
          onUserSelect={handleUserSelect}
          onClose={() => setShowUserSearch(false)}
        />
      )}
      
      {/* Forward Message Dialog */}
      {showForwardDialog && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-md">
            <div className="p-6 space-y-4">
              <div>
                <h2 className="text-lg font-semibold">Forward Message</h2>
                <p className="text-sm text-gray-500">Select where to forward this message</p>
              </div>
              
              {/* Search input */}
              <div>
                <Input
                  placeholder="Search groups, channels, or DMs..."
                  value={forwardSearchQuery}
                  onChange={(e) => {
                    const query = e.target.value.toLowerCase();
                    setForwardSearchQuery(query);
                    
                    if (query.trim()) {
                      // Search across all conversation types
                      const results: ChatConversation[] = [];
                      
                      // Search in channels
                      channels.forEach(c => {
                        if (c.name.toLowerCase().includes(query) || c.display_name?.toLowerCase().includes(query)) {
                          results.push(c);
                        }
                      });
                      
                      // Search in groups
                      groups.forEach(g => {
                        if (g.name.toLowerCase().includes(query) || g.display_name?.toLowerCase().includes(query)) {
                          results.push(g);
                        }
                      });
                      
                      // Search in DMs
                      directMessages.forEach(dm => {
                        if (dm.name.toLowerCase().includes(query) || 
                            dm.display_name?.toLowerCase().includes(query) ||
                            dm.other_user?.toLowerCase().includes(query)) {
                          results.push(dm);
                        }
                      });
                      
                      setForwardSearchResults(results);
                    } else {
                      setForwardSearchResults([]);
                    }
                  }}
                  className="w-full"
                />
              </div>
              
              {/* Search results */}
              {forwardSearchResults.length > 0 && (
                <div className="max-h-64 overflow-y-auto border rounded-lg">
                  {forwardSearchResults.map((conv) => (
                    <div
                      key={`${conv.type}-${conv.id}`}
                      onClick={() => setForwardingTo(conv)}
                      className={`p-3 border-b cursor-pointer hover:bg-gray-50 flex items-center space-x-3 ${
                        forwardingTo?.id === conv.id && forwardingTo?.type === conv.type
                          ? 'bg-blue-50 border-blue-300'
                          : ''
                      }`}
                    >
                      {conv.type === 'direct_message' ? (
                        <User className="w-5 h-5 text-gray-500" />
                      ) : conv.type === 'private_group' ? (
                        <Lock className="w-5 h-5 text-gray-500" />
                      ) : (
                        <Hash className="w-5 h-5 text-gray-500" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{conv.display_name || conv.name}</p>
                        <p className="text-xs text-gray-500">
                          {conv.type === 'direct_message'
                            ? `DM with ${conv.other_user || conv.name}`
                            : conv.type === 'private_group'
                            ? 'Private Group'
                            : 'Channel'}
                        </p>
                      </div>
                      {forwardingTo?.id === conv.id && forwardingTo?.type === conv.type && (
                        <div className="w-4 h-4 rounded-full bg-blue-600"></div>
                      )}
                    </div>
                  ))}
                </div>
              )}
              
              {forwardSearchQuery && forwardSearchResults.length === 0 && (
                <div className="text-center py-4 text-sm text-gray-500">
                  No conversations found
                </div>
              )}
              
              {!forwardSearchQuery && (
                <div className="text-center py-4 text-sm text-gray-500">
                  Start typing to search conversations
                </div>
              )}
              
              {/* Action buttons */}
              <div className="flex gap-2 pt-4">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowForwardDialog(false);
                    setForwardingMessageId(null);
                    setForwardingTo(null);
                  }}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={async () => {
                    if (!forwardingMessageId || !forwardingTo) {
                      toast({
                        title: "Error",
                        description: "Please select a conversation",
                        variant: "destructive"
                      });
                      return;
                    }
                    
                    setIsForwarding(true);
                    try {
                      const message = messages.find(m => m.id === forwardingMessageId);
                      if (!message) {
                        throw new Error("Message not found");
                      }
                      
                      // Prepare forward data with message ID
                      const forwardData = {
                        message_id: forwardingMessageId,
                        target_type: forwardingTo.type === 'direct_message' ? 'dm' : forwardingTo.type === 'private_group' ? 'group' : 'channel',
                        target_id: forwardingTo.type === 'direct_message' ? (forwardingTo.name || forwardingTo.other_user || '') : (forwardingTo.id || '')
                      };
                      
                      console.log('Forwarding message:', forwardData);
                      
                      const response = await fetch('http://localhost:8000/chat/forward-message', {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/json',
                          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                        },
                        body: JSON.stringify(forwardData)
                      });
                      
                      const data = await response.json();
                      if (!response.ok) {
                        throw new Error(data.detail || 'Failed to forward message');
                      }
                      
                      // Store the forwarded message with room information for later operations (delete, edit, etc.)
                      if (data.forwarded_message_id && data.target_room_id) {
                        console.log('✅ Forwarded message created with ID:', data.forwarded_message_id);
                        console.log('📍 Target room ID:', data.target_room_id);
                        
                        // Store the mapping of forwarded message ID to its room ID
                        // This will be used when deleting/editing the forwarded message
                        localStorage.setItem(`fwd_msg_room_${data.forwarded_message_id}`, data.target_room_id);
                      }
                                            toast({
                        title: "Success",
                        description: `Message forwarded to ${forwardingTo.display_name || forwardingTo.name}`
                      });
                      
                      setShowForwardDialog(false);
                      setForwardingMessageId(null);
                      setForwardingTo(null);
                      setForwardSearchQuery('');
                      setForwardSearchResults([]);
                    } catch (error) {
                      console.error('Error forwarding message:', error);
                      toast({
                        title: "Error",
                        description: error instanceof Error ? error.message : 'Failed to forward message',
                        variant: "destructive"
                      });
                    } finally {
                      setIsForwarding(false);
                    }
                  }}
                  disabled={!forwardingTo || isForwarding}
                  className="flex-1"
                >
                  {isForwarding ? 'Forwarding...' : 'Forward'}
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Edit Message Dialog */}
      {showEditDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-auto">
            <div className="p-6 space-y-4">
              <h2 className="text-xl font-bold">Edit Message</h2>
              
              <textarea
                value={editingMessageText}
                onChange={(e) => setEditingMessageText(e.target.value)}
                className="w-full h-32 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                placeholder="Edit your message..."
              />
              
              <div className="flex gap-2">
                <Button
                  onClick={() => {
                    setShowEditDialog(false);
                    setEditingMessageId(null);
                    setEditingMessageText('');
                  }}
                  variant="outline"
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={async () => {
                    if (!editingMessageId || !editingMessageText.trim()) {
                      toast({
                        title: "Error",
                        description: "Message text cannot be empty",
                        variant: "destructive"
                      });
                      return;
                    }
                    
                    setIsEditing(true);
                    try {
                      const response = await fetch('http://localhost:8000/chat/edit-message', {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/json',
                          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                        },
                        body: JSON.stringify({
                          message_id: editingMessageId,
                          text: editingMessageText.trim()
                        })
                      });
                      
                      const data = await response.json();
                      if (!response.ok) {
                        throw new Error(data.detail || 'Failed to edit message');
                      }
                      
                      // Update the message in the local state
                      setMessages(messages.map(msg => 
                        msg.id === editingMessageId 
                          ? { ...msg, text: editingMessageText.trim(), content: editingMessageText.trim(), editedAt: new Date().toISOString() }
                          : msg
                      ));
                      
                      // Also update thread messages if it's a thread message
                      setMessages(prevMessages => 
                        prevMessages.map(msg => ({
                          ...msg,
                          thread_messages: (msg.thread_messages || []).map(tm =>
                            tm.id === editingMessageId
                              ? { ...tm, text: editingMessageText.trim(), content: editingMessageText.trim(), editedAt: new Date().toISOString() }
                              : tm
                          )
                        }))
                      );
                      
                      // Also update threadMessages state if the thread is fetched
                      const parentMsg = messages.find(m => m.thread_messages?.some(tm => tm.id === editingMessageId));
                      if (parentMsg && threadMessages[parentMsg.id]) {
                        setThreadMessages(prev => ({
                          ...prev,
                          [parentMsg.id]: prev[parentMsg.id].map(msg =>
                            msg.id === editingMessageId
                              ? { ...msg, text: editingMessageText.trim(), content: editingMessageText.trim(), editedAt: new Date().toISOString() }
                              : msg
                          )
                        }));
                      }
                      
                      toast({
                        title: "Success",
                        description: "Message edited successfully"
                      });
                      
                      setShowEditDialog(false);
                      setEditingMessageId(null);
                      setEditingMessageText('');
                    } catch (error) {
                      console.error('Error editing message:', error);
                      toast({
                        title: "Error",
                        description: error instanceof Error ? error.message : 'Failed to edit message',
                        variant: "destructive"
                      });
                    } finally {
                      setIsEditing(false);
                    }
                  }}
                  disabled={!editingMessageText.trim() || isEditing}
                  className="flex-1"
                >
                  {isEditing ? 'Editing...' : 'Edit'}
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </ResponsiveLayout>
  );
};

export default EnhancedMessagesWidget;
