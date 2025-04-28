import React from 'react';
import ThreadItem from './ThreadItem';
import { Thread, getAllThreads, getAllChatbots, getThreadsByBotId } from '../data/mockData';

interface ThreadListProps {
  selectedThreadId: string;
  onSelectThread: (threadId: string) => void;
}

const ThreadList: React.FC<ThreadListProps> = ({ selectedThreadId, onSelectThread }) => {
  const chatbots = getAllChatbots();

  return (
    <div className="h-full overflow-y-auto border-r border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">Conversations</h2>
      </div>
      
      <div className="divide-y divide-gray-100">
        {chatbots.map(chatbot => {
          const threads = getThreadsByBotId(chatbot.id);
          
          return (
            <div key={chatbot.id} className="py-2">
              <div className="px-4 py-2">
                <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {chatbot.name}
                </h3>
              </div>
              
              <div>
                {threads.map(thread => (
                  <ThreadItem
                    key={thread.id}
                    thread={thread}
                    isActive={selectedThreadId === thread.id}
                    onClick={() => onSelectThread(thread.id)}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ThreadList;
