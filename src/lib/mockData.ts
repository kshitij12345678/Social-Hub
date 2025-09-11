export interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  bio: string;
  following: number;
  followers: number;
}

export interface Post {
  id: string;
  userId: string;
  user: User;
  content: string;
  image?: string;
  timestamp: string;
  likes: number;
  comments: Comment[];
  shares: number;
  isLiked: boolean;
}

export interface Comment {
  id: string;
  userId: string;
  user: User;
  content: string;
  timestamp: string;
  likes: number;
}

export interface Notification {
  id: string;
  type: 'like' | 'comment' | 'follow' | 'mention';
  from: User;
  content: string;
  timestamp: string;
  read: boolean;
  postId?: string;
}

export interface Message {
  id: string;
  senderId: string;
  receiverId: string;
  content: string;
  timestamp: string;
  read: boolean;
}

export interface Conversation {
  id: string;
  participants: User[];
  lastMessage: Message;
  messages: Message[];
}

// Mock Users
export const mockUsers: User[] = [
  {
    id: '1',
    name: 'Emma Johnson',
    email: 'emma@example.com',
    avatar: '👩‍💼',
    bio: 'UI/UX Designer passionate about creating beautiful experiences',
    following: 245,
    followers: 1200,
  },
  {
    id: '2',
    name: 'Alex Chen',
    email: 'alex@example.com',
    avatar: '👨‍💻',
    bio: 'Full-stack developer & coffee enthusiast',
    following: 180,
    followers: 890,
  },
  {
    id: '3',
    name: 'Sarah Wilson',
    email: 'sarah@example.com',
    avatar: '👩‍🎨',
    bio: 'Digital artist and creative director',
    following: 320,
    followers: 2100,
  },
  {
    id: '4',
    name: 'Mike Rodriguez',
    email: 'mike@example.com',
    avatar: '👨‍📷',
    bio: 'Photographer capturing life\'s beautiful moments',
    following: 150,
    followers: 750,
  },
];

export const currentUser = mockUsers[0];

// Mock Posts
export const mockPosts: Post[] = [
  {
    id: '1',
    userId: '2',
    user: mockUsers[1],
    content: 'Just launched my new portfolio website! Built with React and Tailwind CSS. The design process was incredible - focusing on clean typography and smooth animations. What do you think about the latest web design trends?',
    timestamp: '2 hours ago',
    likes: 24,
    shares: 5,
    isLiked: false,
    comments: [
      {
        id: '1',
        userId: '1',
        user: mockUsers[0],
        content: 'Looks amazing! The animations are so smooth.',
        timestamp: '1 hour ago',
        likes: 3,
      },
      {
        id: '2',
        userId: '3',
        user: mockUsers[2],
        content: 'Love the color palette choice! Very modern.',
        timestamp: '45 minutes ago',
        likes: 2,
      },
    ],
  },
  {
    id: '2',
    userId: '3',
    user: mockUsers[2],
    content: 'Working on a new digital art series inspired by nature and technology. The intersection of organic forms with geometric patterns has always fascinated me. Here\'s a sneak peek of my latest piece! 🎨✨',
    timestamp: '4 hours ago',
    likes: 56,
    shares: 12,
    isLiked: true,
    comments: [
      {
        id: '3',
        userId: '4',
        user: mockUsers[3],
        content: 'This is absolutely stunning! The color transitions are perfect.',
        timestamp: '3 hours ago',
        likes: 8,
      },
    ],
  },
  {
    id: '3',
    userId: '4',
    user: mockUsers[3],
    content: 'Captured this amazing sunset yesterday during my photoshoot. Sometimes the best moments happen when you least expect them. The golden hour never fails to amaze me! 📸🌅',
    timestamp: '1 day ago',
    likes: 89,
    shares: 18,
    isLiked: true,
    comments: [
      {
        id: '4',
        userId: '1',
        user: mockUsers[0],
        content: 'Breathtaking shot! The composition is perfect.',
        timestamp: '20 hours ago',
        likes: 5,
      },
      {
        id: '5',
        userId: '2',
        user: mockUsers[1],
        content: 'The lighting is incredible. What camera did you use?',
        timestamp: '18 hours ago',
        likes: 3,
      },
    ],
  },
];

// Mock Notifications
export const mockNotifications: Notification[] = [
  {
    id: '1',
    type: 'like',
    from: mockUsers[1],
    content: 'liked your post',
    timestamp: '5 minutes ago',
    read: false,
    postId: '1',
  },
  {
    id: '2',
    type: 'comment',
    from: mockUsers[2],
    content: 'commented on your post',
    timestamp: '1 hour ago',
    read: false,
    postId: '2',
  },
  {
    id: '3',
    type: 'follow',
    from: mockUsers[3],
    content: 'started following you',
    timestamp: '2 hours ago',
    read: true,
  },
  {
    id: '4',
    type: 'mention',
    from: mockUsers[1],
    content: 'mentioned you in a comment',
    timestamp: '3 hours ago',
    read: true,
    postId: '3',
  },
];

// Mock Messages
export const mockMessages: Message[] = [
  {
    id: '1',
    senderId: '2',
    receiverId: '1',
    content: 'Hey Emma! Did you see the new design trends article?',
    timestamp: '10:30 AM',
    read: true,
  },
  {
    id: '2',
    senderId: '1',
    receiverId: '2',
    content: 'Yes! The minimalist approach is really interesting.',
    timestamp: '10:45 AM',
    read: true,
  },
  {
    id: '3',
    senderId: '2',
    receiverId: '1',
    content: 'I think we should implement some of those ideas in our next project.',
    timestamp: '10:47 AM',
    read: true,
  },
  {
    id: '4',
    senderId: '1',
    receiverId: '2',
    content: 'Absolutely! Let\'s schedule a meeting to discuss this further.',
    timestamp: '10:50 AM',
    read: false,
  },
];

// Mock Conversations
export const mockConversations: Conversation[] = [
  {
    id: '1',
    participants: [mockUsers[0], mockUsers[1]],
    lastMessage: mockMessages[3],
    messages: mockMessages.filter(msg => 
      (msg.senderId === '1' && msg.receiverId === '2') || 
      (msg.senderId === '2' && msg.receiverId === '1')
    ),
  },
  {
    id: '2',
    participants: [mockUsers[0], mockUsers[2]],
    lastMessage: {
      id: '5',
      senderId: '3',
      receiverId: '1',
      content: 'Thanks for the feedback on my artwork!',
      timestamp: '2:15 PM',
      read: true,
    },
    messages: [
      {
        id: '5',
        senderId: '3',
        receiverId: '1',
        content: 'Thanks for the feedback on my artwork!',
        timestamp: '2:15 PM',
        read: true,
      },
    ],
  },
];