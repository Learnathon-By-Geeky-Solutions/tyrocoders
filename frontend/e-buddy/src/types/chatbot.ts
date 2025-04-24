
// Types for chatbot customization

export interface ChatMessage {
    id: string;
    sender: 'user' | 'bot';
    content: string;
    timestamp: Date;
  }
  
  export interface BotCustomization {
    name: string;
    avatarUrl: string;
    primaryColor: string;
    secondaryColor: string;
    chatBubbleStyle: 'rounded' | 'sharp' | 'bubble';
    welcomeMessage: string;
    font: 'default' | 'modern' | 'classic' | 'playful';
    position: 'right' | 'left';
    responseTemplates: ResponseTemplate[];
    predefinedQuestions: string[];
  }
  
  export interface ResponseTemplate {
    trigger: string;
    response: string;
  }
  
  export interface BotPreview {
    isOpen: boolean;
    messages: ChatMessage[];
    customization: BotCustomization;
  }