import { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, X, ChevronUp, ChevronDown } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BotCustomization, ChatMessage } from '@/types/chatbot';
import { cn } from '@/lib/utils';

interface ChatPreviewProps {
  customization: BotCustomization;
  onClose: () => void;
}

export const ChatPreview = ({ customization, onClose }: ChatPreviewProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isExpanded, setIsExpanded] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Add welcome message when component mounts
    if (messages.length === 0) {
      setMessages([
        {
          id: Date.now().toString(),  // Use dynamic ID based on timestamp
          sender: 'bot',
          content: customization.welcomeMessage,
          timestamp: new Date()
        }
      ]);
      
      // Add predefined questions if available
      if (customization.predefinedQuestions && customization.predefinedQuestions.length > 0) {
        setTimeout(() => {
          setMessages(prev => [
            ...prev,
            {
              id: Date.now().toString(),  // Use dynamic ID based on timestamp
              sender: 'bot',
              content: "Here are some questions you might want to ask:",
              timestamp: new Date()
            }
          ]);
        }, 1000);
      }
    }
  }, [customization, messages.length]);

  useEffect(() => {
    // Scroll to bottom whenever messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = () => {
    if (!userInput.trim()) return;
    
    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      content: userInput,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setUserInput('');
    
    // Simulate bot typing
    setIsTyping(true);
    
    setTimeout(() => {
      // Check for response templates first
      const matchedTemplate = customization.responseTemplates.find(template => 
        userInput.toLowerCase().includes(template.trigger.toLowerCase())
      );
      
      let botResponse = '';
      
      if (matchedTemplate) {
        botResponse = matchedTemplate.response;
      } else {
        // Default responses based on input
        if (userInput.toLowerCase().includes('hello') || userInput.toLowerCase().includes('hi')) {
          botResponse = `Hello there! How can I help you today?`;
        } else if (userInput.toLowerCase().includes('help')) {
          botResponse = `I'm here to help! Please let me know what you're looking for.`;
        } else if (userInput.toLowerCase().includes('thank')) {
          botResponse = `You're welcome! Is there anything else I can help you with?`;
        } else {
          botResponse = `Thank you for your message. I'll connect you with the right information shortly.`;
        }
      }
      
      const botMessage: ChatMessage = {
        id: Date.now().toString(),  // Changed from (Date.now() + 1).toString() to avoid potential conflicts
        sender: 'bot',
        content: botResponse,
        timestamp: new Date()
      };
      
      setIsTyping(false);
      setMessages(prev => [...prev, botMessage]);
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  const getBubbleStyle = (sender: string) => {
    if (sender === 'user') {
      return `bg-gray-100 text-gray-800 ml-auto rounded-t-lg rounded-bl-lg`;
    } else {
      const bgColor = customization.primaryColor || '#9b87f5';
      const bgColorClass = bgColor.startsWith('#') ? '' : bgColor;
      return `${bgColorClass} rounded-t-lg rounded-br-lg ${
        bgColorClass ? '' : 'bg-chatbot-primary'
      } text-white`;
    }
  };

  return (
    <div 
      className={`fixed ${customization.position === 'right' ? 'right-5' : 'left-5'} bottom-5 shadow-lg rounded-lg overflow-hidden flex flex-col z-50 transition-all duration-300 ease-in-out max-w-sm w-full`}
      style={{ 
        fontFamily: 
          customization.font === 'modern' ? 'Inter, sans-serif' :
          customization.font === 'classic' ? 'Georgia, serif' :
          customization.font === 'playful' ? 'Comic Sans MS, cursive' : 'system-ui, sans-serif',
        maxHeight: isExpanded ? '70vh' : '60px' 
      }}
    >
      {/* Header */}
      <div 
        className="p-3 flex justify-between items-center cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
        style={{ 
          backgroundColor: customization.primaryColor || '#9b87f5',
          color: 'white'
        }}
      >
        <div className="flex items-center space-x-2">
          {customization.avatarUrl ? (
            <img src={customization.avatarUrl} alt={customization.name} className="w-8 h-8 rounded-full" />
          ) : (
            <MessageSquare className="w-6 h-6" />
          )}
          <span className="font-medium">{customization.name || 'Chat Bot'}</span>
        </div>
        <div className="flex items-center space-x-2">
          {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
          <X className="w-5 h-5 cursor-pointer" onClick={(e) => {
            e.stopPropagation();
            onClose();
          }} />
        </div>
      </div>
      
      {/* Chat Area - Only shown when expanded */}
      {isExpanded && (
        <>
          <div className="bg-white flex-grow overflow-y-auto p-4 h-80">
            {messages.map((message) => (
              <div 
                key={message.id} 
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-3`}
              >
                <div 
                  className={cn(
                    "max-w-[80%] p-3 animate-slide-in",
                    getBubbleStyle(message.sender),
                    customization.chatBubbleStyle === 'sharp' ? 'rounded-none' : '',
                    customization.chatBubbleStyle === 'bubble' ? 'rounded-full' : ''
                  )}
                  style={message.sender === 'bot' && customization.primaryColor?.startsWith('#') ? {
                    backgroundColor: customization.primaryColor
                  } : {}}
                >
                  {message.content}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start mb-3">
                <div 
                  className={cn(
                    "max-w-[80%] p-3",
                    getBubbleStyle('bot'),
                    customization.chatBubbleStyle === 'sharp' ? 'rounded-none' : '',
                    customization.chatBubbleStyle === 'bubble' ? 'rounded-full' : ''
                  )}
                  style={customization.primaryColor?.startsWith('#') ? {
                    backgroundColor: customization.primaryColor
                  } : {}}
                >
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Predefined Questions */}
            {customization.predefinedQuestions && customization.predefinedQuestions.length > 0 && messages.length <= 2 && (
              <div className="mt-4 space-y-2">
                {customization.predefinedQuestions.map((question, index) => (
                  <Button 
                    key={`question-${index}`}  // Unique key for each question 
                    variant="outline" 
                    className="text-left text-sm p-2 w-full justify-start"
                    onClick={() => {
                      setUserInput(question);
                      setTimeout(() => handleSendMessage(), 100);
                    }}
                  >
                    {question}
                  </Button>
                ))}
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Input Area */}
          <div className="p-3 border-t flex items-center bg-white">
            <Input
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-grow mr-2"
            />
            <Button 
              onClick={handleSendMessage} 
              size="icon"
              style={{ 
                backgroundColor: customization.primaryColor || '#9b87f5'
              }}
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </>
      )}
    </div>
  );
};