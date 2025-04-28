import React from 'react';
import { Thread, getUserById, getChatbotById } from '../data/mockData';
import { Computer, Smartphone } from 'lucide-react';

interface ThreadItemProps {
  thread: Thread;
  isActive: boolean;
  onClick: () => void;
}

const ThreadItem: React.FC<ThreadItemProps> = ({ thread, isActive, onClick }) => {
  const user = getUserById(thread.userId);
  const chatbot = getChatbotById(thread.chatbotId);
  
  // Format the date to display in a friendly format
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div
      className={`p-3 border-b border-gray-100 cursor-pointer transition-colors ${
        isActive ? 'bg-blue-50' : 'hover:bg-gray-50'
      }`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-1">
        <div className="font-medium text-sm text-gray-900">{chatbot?.name}</div>
        <div className="flex items-center">
          {thread.channel === 'web' ? (
            <Computer className="h-3 w-3 text-gray-500 mr-1" />
          ) : (
            <Smartphone className="h-3 w-3 text-gray-500 mr-1" />
          )}
          <span className="text-xs text-gray-500">{formatDate(thread.startDate)}</span>
        </div>
      </div>
      
      <div className="text-xs text-gray-600 mb-2 truncate">{user?.name}</div>
      
      <div className="flex items-center justify-between">
        <div className="text-xs text-gray-500 truncate max-w-[70%]">{thread.lastMessage}</div>
        <div className="bg-brand-blue text-white text-xs px-1.5 py-0.5 rounded-full">
          {thread.messageCount}
        </div>
      </div>
    </div>
  );
};

export default ThreadItem;
