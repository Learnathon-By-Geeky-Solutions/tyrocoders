import { MessageSquare } from 'lucide-react';
import { BotCustomization } from '@/types/chatbot';

interface ChatTriggerProps {
  customization: BotCustomization;
  onClick: () => void;
}

export const ChatTrigger = ({ customization, onClick }: ChatTriggerProps) => {
  return (
    <button
      className="fixed bottom-5 shadow-lg rounded-full p-4 flex items-center justify-center z-50 transition-all hover:scale-105"
      style={{ 
        backgroundColor: customization.primaryColor || '#9b87f5',
        right: customization.position === 'right' ? '20px' : 'auto',
        left: customization.position === 'left' ? '20px' : 'auto'
      }}
      onClick={onClick}
    >
      <MessageSquare className="w-6 h-6 text-white" />
    </button>
  );
};
