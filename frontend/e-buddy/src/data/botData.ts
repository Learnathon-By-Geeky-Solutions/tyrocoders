import { BotCustomization } from "@/types/chatbot";

export interface Bot {
  id: number;
  name: string;
  model: string;
  createdAt: string;
  description: string;
  stats: {
    conversations: number;
    leadGeneration: number;
    conversionRate: number;
    avgResponseTime: string;
    customerSatisfaction: number;
    activeUsers: number;
  };
  performance: {
    date: string;
    conversations: number;
    leads: number;
    sales: number;
  }[];
  customization: BotCustomization;
}

export const dummyBots: Bot[] = [
  {
    id: 1,
    name: 'ShopAssist Pro',
    model: 'GPT-4',
    createdAt: '2024-01-01',
    description:
      'An advanced e-commerce assistant powered by GPT-4, designed to boost sales and enhance customer experience.',
    stats: {
      conversations: 15234,
      leadGeneration: 4521,
      conversionRate: 68,
      avgResponseTime: '1.2s',
      customerSatisfaction: 94,
      activeUsers: 3890,
    },
    performance: [
      { date: '2024-01', conversations: 2400, leads: 1398, sales: 2210 },
      { date: '2024-02', conversations: 1398, leads: 2800, sales: 2908 },
      { date: '2024-03', conversations: 9800, leads: 3908, sales: 4800 },
      { date: '2024-04', conversations: 3908, leads: 4800, sales: 3800 },
      { date: '2024-05', conversations: 4800, leads: 3800, sales: 4300 },
    ],
    customization: {
      name: 'ShopAssist Pro',
      avatarUrl: 'https://api.dicebear.com/6.x/bottts/svg?seed=shop',
      primaryColor: '#4F46E5',
      secondaryColor: '#818CF8',
      chatBubbleStyle: 'rounded',
      welcomeMessage: 'Welcome to our shop! How can I help you find the perfect product today?',
      font: 'modern',
      position: 'right',
      responseTemplates: [
        {
          trigger: 'price',
          response: 'Our products range from $19.99 to $199.99 depending on the model and features. Can you tell me what you\'re looking for specifically?'
        },
        {
          trigger: 'shipping',
          response: 'We offer free shipping on all orders over $50. Standard delivery takes 3-5 business days, and express shipping (2-day) is available for an additional $9.99.'
        },
        {
          trigger: 'return',
          response: 'We have a 30-day satisfaction guarantee. If you\'re not happy with your purchase, you can return it within 30 days for a full refund.'
        }
      ],
      predefinedQuestions: [
        'What are your shipping options?',
        'Do you have a return policy?',
        'What\'s your best-selling product?',
        'Are there any current promotions?'
      ]
    }
  },
  {
    id: 2,
    name: 'SupportBot',
    model: 'GPT-3.5',
    createdAt: '2024-02-15',
    description:
      'A dedicated customer support assistant that handles common questions and troubleshooting issues.',
    stats: {
      conversations: 24567,
      leadGeneration: 2104,
      conversionRate: 42,
      avgResponseTime: '0.8s',
      customerSatisfaction: 87,
      activeUsers: 6789,
    },
    performance: [
      { date: '2024-01', conversations: 3200, leads: 980, sales: 450 },
      { date: '2024-02', conversations: 4100, leads: 1200, sales: 520 },
      { date: '2024-03', conversations: 5700, leads: 1540, sales: 670 },
      { date: '2024-04', conversations: 5900, leads: 1620, sales: 710 },
      { date: '2024-05', conversations: 6100, leads: 1800, sales: 780 },
    ],
    customization: {
      name: 'Support Helper',
      avatarUrl: 'https://api.dicebear.com/6.x/bottts/svg?seed=support',
      primaryColor: '#10B981',
      secondaryColor: '#34D399',
      chatBubbleStyle: 'bubble',
      welcomeMessage: 'Hello! I\'m your support assistant. How can I help you solve your issue today?',
      font: 'default',
      position: 'right',
      responseTemplates: [
        {
          trigger: 'password',
          response: 'To reset your password, please click on the "Forgot Password" link on the login page and follow the instructions sent to your email.'
        },
        {
          trigger: 'account',
          response: 'For account-related issues, please provide your account email address and I can look up the status for you.'
        }
      ],
      predefinedQuestions: [
        'How do I reset my password?',
        'Where can I update my account details?',
        'Is there a way to cancel my subscription?'
      ]
    }
  }
];
