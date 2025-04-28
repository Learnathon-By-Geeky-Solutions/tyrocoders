import React from 'react';
import { Message } from '../data/mockData';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.senderType === 'user';
  
  // Format the timestamp
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className="flex flex-col max-w-[70%]">
        <div
          className={`p-3 rounded-lg ${
            isUser 
              ? 'bg-gray-100 text-gray-800' 
              : 'bg-white text-gray-800 border border-gray-100 shadow-sm'
          }`}
        >
          <p className="text-sm">{message.content}</p>
        </div>
        <span className="text-xs text-gray-500 mt-1 self-end">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
};

export default MessageBubble;
