"use client"

import React, { useState } from 'react';
import ThreadList from '@/components/ThreadList';
import MessagePanel from '@/components/MessagePanel';
import { getAllThreads } from '../data/mockData';

const ChatPanel: React.FC = () => {
  const threads = getAllThreads();
  const [selectedThreadId, setSelectedThreadId] = useState(threads.length > 0 ? threads[0].id : '');

  return (
    <div className="w-full mx-auto bg-white -lg shadow-md overflow-hidden">
      <div className="flex h-full">
        <div className="w-1/3 border-r border-gray-200">
          <ThreadList 
            selectedThreadId={selectedThreadId} 
            onSelectThread={setSelectedThreadId} 
          />
        </div>
        <div className="w-2/3">
          <MessagePanel threadId={selectedThreadId} />
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
