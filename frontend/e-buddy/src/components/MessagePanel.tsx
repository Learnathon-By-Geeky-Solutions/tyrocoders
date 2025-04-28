import React from 'react';
import MetadataBar from '@/components/MetadataBar';
import MessageBubble from './MessageBubble';
import { getThreadById, getMessagesByThreadId } from '../data/mockData';

interface MessagePanelProps {
  threadId: string;
}

const MessagePanel: React.FC<MessagePanelProps> = ({ threadId }) => {
  const thread = getThreadById(threadId);
  const messages = getMessagesByThreadId(threadId);
  
  if (!thread) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50">
        <p className="text-gray-500">Select a conversation to view messages</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <MetadataBar thread={thread} />
      
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.map(message => (
          <MessageBubble key={message.id} message={message} />
        ))}
      </div>
    </div>
  );
};

export default MessagePanel;
