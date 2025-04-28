export interface User {
    id: string;
    name: string;
    avatar?: string;
  }
  
  export interface Chatbot {
    id: string;
    name: string;
    logo?: string;
  }
  
  export interface Message {
    id: string;
    threadId: string;
    senderId: string;
    senderType: 'user' | 'bot';
    content: string;
    timestamp: string;
  }
  
  export interface Thread {
    id: string;
    chatbotId: string;
    userId: string;
    startDate: string;
    messageCount: number;
    lastMessage: string;
    feedback?: 'positive' | 'negative' | 'neutral';
    confidenceScore: number;
    status: 'live' | 'ended';
    channel: 'web' | 'mobile';
  }
  
  // Users
  const users: User[] = [
    { id: 'u1', name: 'John Smith', avatar: '/placeholder.svg' },
    { id: 'u2', name: 'Emily Davis', avatar: '/placeholder.svg' },
    { id: 'u3', name: 'Michael Brown', avatar: '/placeholder.svg' },
  ];
  
  // Chatbots
  const chatbots: Chatbot[] = [
    { id: 'c1', name: 'ShopBot', logo: '/placeholder.svg' },
    { id: 'c2', name: 'My Store Chatbot', logo: '/placeholder.svg' },
  ];
  
  // Threads
  const threads: Thread[] = [
    {
      id: 't1',
      chatbotId: 'c1',
      userId: 'u1',
      startDate: '2025-04-23T14:30:00Z',
      messageCount: 5,
      lastMessage: 'Thank you for your help!',
      feedback: 'positive',
      confidenceScore: 95,
      status: 'ended',
      channel: 'web',
    },
    {
      id: 't2',
      chatbotId: 'c1',
      userId: 'u2',
      startDate: '2025-04-24T09:15:00Z',
      messageCount: 3,
      lastMessage: 'Where can I find more information?',
      feedback: 'neutral',
      confidenceScore: 85,
      status: 'ended',
      channel: 'mobile',
    },
    {
      id: 't3',
      chatbotId: 'c2',
      userId: 'u3',
      startDate: '2025-04-25T11:00:00Z',
      messageCount: 8,
      lastMessage: 'Is this item available in blue?',
      feedback: 'neutral',
      confidenceScore: 100,
      status: 'live',
      channel: 'web',
    },
    {
      id: 't4',
      chatbotId: 'c2',
      userId: 'u1',
      startDate: '2025-04-22T16:45:00Z',
      messageCount: 4,
      lastMessage: 'I need a refund for my order.',
      feedback: 'negative',
      confidenceScore: 90,
      status: 'ended',
      channel: 'web',
    },
  ];
  
  // Messages for Thread 1
  const messagesT1: Message[] = [
    {
      id: 'm1',
      threadId: 't1',
      senderId: 'u1',
      senderType: 'user',
      content: 'Hello, I need help finding a product.',
      timestamp: '2025-04-23T14:30:00Z',
    },
    {
      id: 'm2',
      threadId: 't1',
      senderId: 'c1',
      senderType: 'bot',
      content: 'Hi John! I\'d be happy to help you find a product. What are you looking for?',
      timestamp: '2025-04-23T14:30:10Z',
    },
    {
      id: 'm3',
      threadId: 't1',
      senderId: 'u1',
      senderType: 'user',
      content: 'I\'m looking for a pair of wireless headphones.',
      timestamp: '2025-04-23T14:30:30Z',
    },
    {
      id: 'm4',
      threadId: 't1',
      senderId: 'c1',
      senderType: 'bot',
      content: 'We have several wireless headphones available. Our most popular models are the SoundWave Pro and the AudioPlus Elite. Would you like to see details for either of these?',
      timestamp: '2025-04-23T14:30:45Z',
    },
    {
      id: 'm5',
      threadId: 't1',
      senderId: 'u1',
      senderType: 'user',
      content: 'Thank you for your help!',
      timestamp: '2025-04-23T14:31:15Z',
    },
  ];
  
  // Messages for Thread 2
  const messagesT2: Message[] = [
    {
      id: 'm6',
      threadId: 't2',
      senderId: 'u2',
      senderType: 'user',
      content: 'Do you offer free shipping?',
      timestamp: '2025-04-24T09:15:00Z',
    },
    {
      id: 'm7',
      threadId: 't2',
      senderId: 'c1',
      senderType: 'bot',
      content: 'Yes, we offer free shipping on orders over $50.',
      timestamp: '2025-04-24T09:15:10Z',
    },
    {
      id: 'm8',
      threadId: 't2',
      senderId: 'u2',
      senderType: 'user',
      content: 'Where can I find more information?',
      timestamp: '2025-04-24T09:15:30Z',
    },
  ];
  
  // Messages for Thread 3
  const messagesT3: Message[] = [
    {
      id: 'm9',
      threadId: 't3',
      senderId: 'u3',
      senderType: 'user',
      content: 'Hi, I\'m interested in the leather jacket.',
      timestamp: '2025-04-25T11:00:00Z',
    },
    {
      id: 'm10',
      threadId: 't3',
      senderId: 'c2',
      senderType: 'bot',
      content: 'Hello Michael! The leather jacket is one of our best sellers. It comes in black, brown, and tan.',
      timestamp: '2025-04-25T11:00:15Z',
    },
    {
      id: 'm11',
      threadId: 't3',
      senderId: 'u3',
      senderType: 'user',
      content: 'What sizes do you have available?',
      timestamp: '2025-04-25T11:00:45Z',
    },
    {
      id: 'm12',
      threadId: 't3',
      senderId: 'c2',
      senderType: 'bot',
      content: 'We currently have sizes S, M, L, and XL in stock.',
      timestamp: '2025-04-25T11:01:00Z',
    },
    {
      id: 'm13',
      threadId: 't3',
      senderId: 'u3',
      senderType: 'user',
      content: 'Great, I wear a medium. How much is the jacket?',
      timestamp: '2025-04-25T11:01:30Z',
    },
    {
      id: 'm14',
      threadId: 't3',
      senderId: 'c2',
      senderType: 'bot',
      content: 'The leather jacket is $199.99. We\'re currently offering a 10% discount for first-time customers.',
      timestamp: '2025-04-25T11:01:45Z',
    },
    {
      id: 'm15',
      threadId: 't3',
      senderId: 'u3',
      senderType: 'user',
      content: 'That sounds good. Does it come in blue?',
      timestamp: '2025-04-25T11:02:15Z',
    },
    {
      id: 'm16',
      threadId: 't3',
      senderId: 'c2',
      senderType: 'bot',
      content: 'I\'m sorry, we don\'t currently have the leather jacket in blue. Would you like me to check if we have any other jacket styles available in blue?',
      timestamp: '2025-04-25T11:02:30Z',
    },
  ];
  
  // Messages for Thread 4
  const messagesT4: Message[] = [
    {
      id: 'm17',
      threadId: 't4',
      senderId: 'u1',
      senderType: 'user',
      content: 'I received the wrong item in my order #12345.',
      timestamp: '2025-04-22T16:45:00Z',
    },
    {
      id: 'm18',
      threadId: 't4',
      senderId: 'c2',
      senderType: 'bot',
      content: 'I\'m sorry to hear that, John. I\'d be happy to help you with this issue.',
      timestamp: '2025-04-22T16:45:15Z',
    },
    {
      id: 'm19',
      threadId: 't4',
      senderId: 'u1',
      senderType: 'user',
      content: 'I ordered a red shirt but received a blue one.',
      timestamp: '2025-04-22T16:45:45Z',
    },
    {
      id: 'm20',
      threadId: 't4',
      senderId: 'c2',
      senderType: 'bot',
      content: 'I understand. I\'ve checked your order and can process a return for you. Would you like a refund or a replacement in the correct color?',
      timestamp: '2025-04-22T16:46:00Z',
    },
    {
      id: 'm21',
      threadId: 't4',
      senderId: 'u1',
      senderType: 'user',
      content: 'I need a refund for my order.',
      timestamp: '2025-04-22T16:46:30Z',
    },
  ];
  
  // Combine all messages
  const messages: Message[] = [...messagesT1, ...messagesT2, ...messagesT3, ...messagesT4];
  
  // Get user by ID
  export const getUserById = (id: string): User | undefined => {
    return users.find(user => user.id === id);
  };
  
  // Get chatbot by ID
  export const getChatbotById = (id: string): Chatbot | undefined => {
    return chatbots.find(bot => bot.id === id);
  };
  
  // Get thread by ID
  export const getThreadById = (id: string): Thread | undefined => {
    return threads.find(thread => thread.id === id);
  };
  
  // Get all threads
  export const getAllThreads = (): Thread[] => {
    return threads;
  };
  
  // Get messages by thread ID
  export const getMessagesByThreadId = (threadId: string): Message[] => {
    return messages.filter(message => message.threadId === threadId);
  };
  
  // Group threads by chatbot ID
  export const getThreadsByBotId = (botId: string): Thread[] => {
    return threads.filter(thread => thread.chatbotId === botId);
  };
  
  // Get all chatbots
  export const getAllChatbots = (): Chatbot[] => {
    return chatbots;
  };
  