# SocialHub - Modern Social Media Web App

A beautiful, responsive social media frontend built with React.js, featuring an elegant pastel color palette and smooth animations.

## 🎨 Features

### Pages & Components
- **Landing Page** - Welcome section with gradient background and call-to-action buttons
- **Authentication** - Signup and Login forms with validation and Google integration
- **Home Feed** - Social posts with like, comment, and share functionality
- **Profile Page** - User profiles with editable fields and post grid/list view
- **Notifications** - Real-time notifications with filtering and mark as read
- **Messages** - Real-time chat interface with conversation sidebar
- **Responsive Design** - Mobile-first design that works on all devices

### Design System
- **Pastel Color Palette**: 
  - Pastel Blue (#A8DADC)
  - Pastel Pink (#FAD4D4) 
  - Pastel Green (#B8E1C8)
  - Light Gray (#F1FAEE)
  - Soft Yellow (#FFE5B4)
- **Typography**: Poppins font for clean, modern text
- **Animations**: Smooth transitions and hover effects
- **Components**: Reusable UI components with variants

## 🚀 Getting Started

### Prerequisites
- Node.js (16.x or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd socialhub
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:8080`

## 📁 Project Structure

```
src/
├── components/
│   ├── ui/                     # Reusable UI components
│   │   ├── navbar.tsx         # Navigation component
│   │   ├── feed-post-card.tsx # Post display component
│   │   ├── notification-card.tsx # Notification item
│   │   ├── message-bubble.tsx  # Chat message component
│   │   └── user-profile.tsx   # Profile component
│   ├── forms/                 # Form components
│   │   ├── signup-form.tsx    # Registration form
│   │   └── login-form.tsx     # Login form
│   └── layout/                # Layout components
│       └── responsive-layout.tsx # Main layout wrapper
├── pages/                     # Page components
│   ├── Landing.tsx           # Landing page
│   ├── Login.tsx             # Login page
│   ├── Signup.tsx            # Signup page
│   ├── Feed.tsx              # Home feed
│   ├── Profile.tsx           # User profile
│   ├── Notifications.tsx     # Notifications page
│   └── Messages.tsx          # Chat interface
├── lib/
│   └── mockData.ts           # Mock data for development
├── hooks/                    # Custom React hooks
└── assets/                   # Static assets
```

## 🎯 Key Components

### Navbar
- Responsive navigation with active state indicators
- User menu with profile information
- Mobile-friendly bottom navigation

### FeedPostCard  
- Interactive post cards with like, comment, share
- Collapsible comments section
- User avatars and timestamps

### NotificationCard
- Different notification types (like, comment, follow, mention)
- Read/unread states with visual indicators
- Action buttons for quick responses

### MessageBubble
- Chat bubbles with sent/received styling
- Read receipts and timestamps
- Responsive design for mobile and desktop

### UserProfile
- Editable profile information
- Stats display (followers, following)
- Post grid and list view toggle

## 🛠 Technology Stack

- **Frontend**: React 18 with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: shadcn/ui component library
- **Routing**: React Router v6
- **State Management**: React hooks and context
- **Build Tool**: Vite
- **Icons**: Lucide React

## 📱 Responsive Design

The app is fully responsive with:
- Mobile-first approach
- Breakpoint-specific layouts
- Touch-friendly interactions
- Optimized navigation for small screens

## 🎨 Design Features

- **Pastel Color Scheme**: Soft, professional colors throughout
- **Smooth Animations**: CSS transitions and keyframe animations
- **Modern Typography**: Poppins font family
- **Card-based Layout**: Consistent card components
- **Hover Effects**: Interactive feedback on all clickable elements

## 🔧 Development

### Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Customization
- Colors can be modified in `src/index.css` (CSS variables)
- Component variants in individual component files
- Animations defined in `tailwind.config.ts`

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](issues).

---

Built with ❤️ using React.js and Tailwind CSS