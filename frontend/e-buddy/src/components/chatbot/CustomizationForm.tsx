import { useState } from 'react';
import { BotCustomization, ResponseTemplate } from '@/types/chatbot';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Plus, X } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent } from '@/components/ui/card';
import { motion } from 'framer-motion';

interface CustomizationFormProps {
  customization: BotCustomization;
  onChange: (customization: BotCustomization) => void;
}

export const CustomizationForm = ({ customization, onChange }: CustomizationFormProps) => {
  const [newTrigger, setNewTrigger] = useState('');
  const [newResponse, setNewResponse] = useState('');
  const [newPredefinedQuestion, setNewPredefinedQuestion] = useState('');

  const handleResponseTemplateAdd = () => {
    if (newTrigger.trim() && newResponse.trim()) {
      const newTemplate: ResponseTemplate = {
        trigger: newTrigger.trim(),
        response: newResponse.trim(),
      };
      onChange({
        ...customization,
        responseTemplates: [...customization.responseTemplates, newTemplate],
      });
      setNewTrigger('');
      setNewResponse('');
    }
  };

  const handleResponseTemplateDelete = (indexToDelete: number) => {
    onChange({
      ...customization,
      responseTemplates: customization.responseTemplates.filter((_, idx) => idx !== indexToDelete),
    });
  };

  const handlePredefinedQuestionAdd = () => {
    if (newPredefinedQuestion.trim()) {
      onChange({
        ...customization,
        predefinedQuestions: [...customization.predefinedQuestions, newPredefinedQuestion.trim()],
      });
      setNewPredefinedQuestion('');
    }
  };

  const handlePredefinedQuestionDelete = (idxToDelete: number) => {
    onChange({
      ...customization,
      predefinedQuestions: customization.predefinedQuestions.filter((_, idx) => idx !== idxToDelete),
    });
  };

  const sectionVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <div className="space-y-8 p-4 bg-gray-50 rounded-lg">
      {/* Appearance Section */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={sectionVariants}
        transition={{ duration: 0.4 }}
      >
        <Card className="border-2 border-primary-300 shadow-lg hover:shadow-xl transition-shadow">
          <CardContent className="p-8">
            <h4 className="text-2xl font-semibold mb-6 border-b-2 pb-2 text-primary-600">
              Appearance
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Bot Name */}
              <div className="space-y-2">
                <Label htmlFor="bot-name">Bot Name</Label>
                <Input
                  id="bot-name"
                  value={customization.name}
                  onChange={(e) =>
                    onChange({ ...customization, name: e.target.value })
                  }
                  className="focus:ring-2 focus:ring-primary-400"
                />
              </div>

              {/* Avatar URL */}
              <div className="space-y-2">
                <Label htmlFor="avatar-url">Avatar URL</Label>
                <Input
                  id="avatar-url"
                  value={customization.avatarUrl}
                  onChange={(e) =>
                    onChange({ ...customization, avatarUrl: e.target.value })
                  }
                  placeholder="https://example.com/avatar.png"
                  className="focus:ring-2 focus:ring-primary-400"
                />
              </div>

              {/* Primary Color */}
              <div className="space-y-2">
                <Label htmlFor="primary-color">Primary Color</Label>
                <div className="flex items-center gap-3">
                  <input
                    id="primary-color"
                    type="color"
                    value={customization.primaryColor}
                    onChange={(e) =>
                      onChange({
                        ...customization,
                        primaryColor: e.target.value,
                      })
                    }
                    className="w-10 h-10 border-2 rounded-lg"
                  />
                  <Input
                    value={customization.primaryColor}
                    onChange={(e) =>
                      onChange({
                        ...customization,
                        primaryColor: e.target.value,
                      })
                    }
                    className="flex-grow focus:ring-2 focus:ring-primary-400"
                  />
                </div>
              </div>

              {/* Secondary Color */}
              <div className="space-y-2">
                <Label htmlFor="secondary-color">Secondary Color</Label>
                <div className="flex items-center gap-3">
                  <input
                    id="secondary-color"
                    type="color"
                    value={customization.secondaryColor}
                    onChange={(e) =>
                      onChange({
                        ...customization,
                        secondaryColor: e.target.value,
                      })
                    }
                    className="w-10 h-10 border-2 rounded-lg"
                  />
                  <Input
                    value={customization.secondaryColor}
                    onChange={(e) =>
                      onChange({
                        ...customization,
                        secondaryColor: e.target.value,
                      })
                    }
                    className="flex-grow focus:ring-2 focus:ring-secondary-400"
                  />
                </div>
              </div>

              {/* Chat Bubble Style */}
              <div className="space-y-2">
                <Label htmlFor="chat-bubble-style">Chat Bubble Style</Label>
                <Select
                  value={customization.chatBubbleStyle}
                  onValueChange={(value) =>
                    onChange({
                      ...customization,
                      chatBubbleStyle: value as any,
                    })
                  }
                >
                  <SelectTrigger className="focus:ring-2 focus:ring-primary-400">
                    <SelectValue placeholder="Select a style" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="rounded">Rounded</SelectItem>
                    <SelectItem value="sharp">Sharp</SelectItem>
                    <SelectItem value="bubble">Bubble</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Font Style */}
              <div className="space-y-2">
                <Label htmlFor="font">Font Style</Label>
                <Select
                  value={customization.font}
                  onValueChange={(value) =>
                    onChange({ ...customization, font: value as any })
                  }
                >
                  <SelectTrigger className="focus:ring-2 focus:ring-primary-400">
                    <SelectValue placeholder="Select a font" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">Default</SelectItem>
                    <SelectItem value="modern">Modern</SelectItem>
                    <SelectItem value="classic">Classic</SelectItem>
                    <SelectItem value="playful">Playful</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Position */}
              <div className="space-y-2">
                <Label htmlFor="position">Position</Label>
                <Select
                  value={customization.position}
                  onValueChange={(value) =>
                    onChange({ ...customization, position: value as any })
                  }
                >
                  <SelectTrigger className="focus:ring-2 focus:ring-primary-400">
                    <SelectValue placeholder="Select position" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="right">Right</SelectItem>
                    <SelectItem value="left">Left</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Conversation Section */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={sectionVariants}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <Card className="border-2 border-secondary-300 shadow-lg hover:shadow-xl transition-shadow">
          <CardContent className="p-8">
            <h4 className="text-2xl font-semibold mb-6 border-b-2 pb-2 text-secondary-600">
              Conversation
            </h4>
            <div className="space-y-6">
              {/* Welcome Message */}
              <div className="space-y-2">
                <Label htmlFor="welcome-message">Welcome Message</Label>
                <Textarea
                  id="welcome-message"
                  value={customization.welcomeMessage}
                  onChange={(e) =>
                    onChange({
                      ...customization,
                      welcomeMessage: e.target.value,
                    })
                  }
                  rows={4}
                  className="focus:ring-2 focus:ring-secondary-400 rounded-lg"
                />
              </div>

              {/* Predefined Questions */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label>Predefined Questions</Label>
                  <div className="flex items-center space-x-2">
                    <Input
                      value={newPredefinedQuestion}
                      onChange={(e) => setNewPredefinedQuestion(e.target.value)}
                      placeholder="Add a question"
                      className="w-64 focus:ring-2 focus:ring-secondary-400"
                    />
                    <Button
                      onClick={handlePredefinedQuestionAdd}
                      type="button"
                      className="flex items-center space-x-1"
                    >
                      <Plus className="w-4 h-4" />
                      <span>Add</span>
                    </Button>
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {customization.predefinedQuestions.map((q, i) => (
                    <motion.div
                      key={i}
                      className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm"
                      whileHover={{ scale: 1.02 }}
                    >
                      <span>{q}</span>
                      <button
                        onClick={() => handlePredefinedQuestionDelete(i)}
                        className="text-red-500"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Response Templates */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label>Response Templates</Label>
                  <div className="flex items-center space-x-2">
                    <Input
                      value={newTrigger}
                      onChange={(e) => setNewTrigger(e.target.value)}
                      placeholder="Trigger phrase"
                      className="w-48 focus:ring-2 focus:ring-secondary-400"
                    />
                    <Textarea
                      value={newResponse}
                      onChange={(e) => setNewResponse(e.target.value)}
                      placeholder="Response text"
                      rows={2}
                      className="w-64 focus:ring-2 focus:ring-secondary-400 rounded-lg"
                    />
                    <Button
                      onClick={handleResponseTemplateAdd}
                      type="button"
                      className="flex items-center space-x-1"
                    >
                      <Plus className="w-4 h-4" />
                      <span>Add</span>
                    </Button>
                  </div>
                </div>
                <div className="space-y-3">
                  {customization.responseTemplates.map((tpl, idx) => (
                    <motion.div
                      key={idx}
                      className="p-4 bg-white rounded-lg shadow-sm"
                      whileHover={{ scale: 1.02 }}
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-medium">
                          Trigger: "{tpl.trigger}"
                        </span>
                        <button
                          onClick={() => handleResponseTemplateDelete(idx)}
                          className="text-red-500"
                        >
                          <X className="w-5 h-5" />
                        </button>
                      </div>
                      <p className="text-gray-600">
                        Response: "{tpl.response}"
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
