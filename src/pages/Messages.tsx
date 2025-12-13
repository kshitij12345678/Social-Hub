import React from 'react';
import { useLocation } from 'react-router-dom';
import EnhancedMessagesWidget from '@/components/chat/EnhancedMessagesWidget';

const Messages: React.FC = () => {
  const location = useLocation();
  
  // Get the group to open from navigation state
  const openGroup = location.state?.openGroup;

  return (
    <div className="h-full">
      <EnhancedMessagesWidget openGroup={openGroup} />
    </div>
  );
};

export default Messages;