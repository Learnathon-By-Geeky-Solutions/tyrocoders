import React from 'react';
import { Thread, getChatbotById, getUserById } from '../data/mockData';
import { Computer, Smartphone, ThumbsUp, ThumbsDown } from 'lucide-react';

interface MetadataBarProps {
  thread: Thread;
}

const MetadataBar: React.FC<MetadataBarProps> = ({ thread }) => {
  const user = getUserById(thread.userId);
  const chatbot = getChatbotById(thread.chatbotId);

  return (
    <div className="bg-white py-3 px-4 border-b border-gray-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className="h-8 w-8 rounded-full bg-gray-200 mr-3 flex items-center justify-center">
            <span className="font-medium text-xs">{chatbot?.name.substring(0, 2)}</span>
          </div>
          <div>
            <h3 className="font-medium text-sm text-gray-900">{chatbot?.name}</h3>
            <div className="flex items-center">
              <span className="text-xs text-gray-500 mr-2">{user?.name}</span>
              {thread.channel === 'web' ? (
                <Computer className="h-3 w-3 text-gray-500" />
              ) : (
                <Smartphone className="h-3 w-3 text-gray-500" />
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            {thread.feedback === 'positive' ? (
              <ThumbsUp className="h-4 w-4 text-green-500 mr-1" />
            ) : thread.feedback === 'negative' ? (
              <ThumbsDown className="h-4 w-4 text-red-500 mr-1" />
            ) : (
              <div className="flex items-center">
                <ThumbsUp className="h-4 w-4 text-gray-300 mr-1" />
                <ThumbsDown className="h-4 w-4 text-gray-300" />
              </div>
            )}
            <span className="text-xs text-gray-500">
              {thread.feedback ? thread.feedback.charAt(0).toUpperCase() + thread.feedback.slice(1) : 'Neutral'}
            </span>
          </div>
          
          <div className="flex items-center">
            <span className="text-xs font-medium px-1.5 py-0.5 rounded-full bg-gray-100">
              {thread.confidenceScore}%
            </span>
          </div>
          
          <div className="flex items-center">
            <span
              className={`text-xs px-1.5 py-0.5 rounded-full ${
                thread.status === 'live'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {thread.status.charAt(0).toUpperCase() + thread.status.slice(1)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetadataBar;
