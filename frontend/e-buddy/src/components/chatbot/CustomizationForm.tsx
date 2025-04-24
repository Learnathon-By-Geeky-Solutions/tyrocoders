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
        response: newResponse.trim()
      };
      
      onChange({
        ...customization,
        responseTemplates: [...customization.responseTemplates, newTemplate]
      });
      
      setNewTrigger('');
      setNewResponse('');
    }
  };

  const handleResponseTemplateDelete = (indexToDelete: number) => {
    onChange({
      ...customization,
      responseTemplates: customization.responseTemplates.filter((_, index) => index !== indexToDelete)
    });
  };

  const handlePredefinedQuestionAdd = () => {
    if (newPredefinedQuestion.trim()) {
      onChange({
        ...customization,
        predefinedQuestions: [...customization.predefinedQuestions, newPredefinedQuestion.trim()]
      });
      setNewPredefinedQuestion('');
    }
  };

  const handlePredefinedQuestionDelete = (indexToDelete: number) => {
    onChange({
      ...customization,
      predefinedQuestions: customization.predefinedQuestions.filter((_, index) => index !== indexToDelete)
    });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="p-6">
          <h4 className="font-medium text-lg mb-4">Appearance</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="bot-name">Bot Name</Label>
              <Input
                id="bot-name"
                value={customization.name}
                onChange={(e) => onChange({ ...customization, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="avatar-url">Avatar URL</Label>
              <Input
                id="avatar-url"
                value={customization.avatarUrl}
                onChange={(e) => onChange({ ...customization, avatarUrl: e.target.value })}
                placeholder="https://example.com/avatar.png"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="primary-color">Primary Color</Label>
              <div className="flex items-center gap-2">
                <input
                  id="primary-color"
                  type="color"
                  value={customization.primaryColor}
                  onChange={(e) => onChange({ ...customization, primaryColor: e.target.value })}
                  className="w-10 h-10 p-1 border rounded"
                />
                <Input
                  value={customization.primaryColor}
                  onChange={(e) => onChange({ ...customization, primaryColor: e.target.value })}
                  className="flex-grow"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="secondary-color">Secondary Color</Label>
              <div className="flex items-center gap-2">
                <input
                  id="secondary-color"
                  type="color"
                  value={customization.secondaryColor}
                  onChange={(e) => onChange({ ...customization, secondaryColor: e.target.value })}
                  className="w-10 h-10 p-1 border rounded"
                />
                <Input
                  value={customization.secondaryColor}
                  onChange={(e) => onChange({ ...customization, secondaryColor: e.target.value })}
                  className="flex-grow"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="chat-bubble-style">Chat Bubble Style</Label>
              <Select
                value={customization.chatBubbleStyle}
                onValueChange={(value) => onChange({ ...customization, chatBubbleStyle: value as 'rounded' | 'sharp' | 'bubble' })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a style" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="rounded">Rounded</SelectItem>
                  <SelectItem value="sharp">Sharp</SelectItem>
                  <SelectItem value="bubble">Bubble</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="font">Font Style</Label>
              <Select
                value={customization.font}
                onValueChange={(value) => onChange({ ...customization, font: value as 'default' | 'modern' | 'classic' | 'playful' })}
              >
                <SelectTrigger>
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
            <div className="space-y-2">
              <Label htmlFor="position">Position</Label>
              <Select
                value={customization.position}
                onValueChange={(value) => onChange({ ...customization, position: value as 'right' | 'left' })}
              >
                <SelectTrigger>
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

      <Card>
        <CardContent className="p-6">
          <h4 className="font-medium text-lg mb-4">Conversation</h4>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="welcome-message">Welcome Message</Label>
              <Textarea
                id="welcome-message"
                value={customization.welcomeMessage}
                onChange={(e) => onChange({ ...customization, welcomeMessage: e.target.value })}
                rows={3}
              />
            </div>

            <div className="space-y-4">
              <Label>Predefined Questions</Label>
              <div className="flex items-center gap-2">
                <Input
                  value={newPredefinedQuestion}
                  onChange={(e) => setNewPredefinedQuestion(e.target.value)}
                  placeholder="Add a predefined question"
                  className="flex-grow"
                />
                <Button className="text-white" onClick={handlePredefinedQuestionAdd} type="button">
                  <Plus className="w-4 h-4 mr-2" />
                  Add
                </Button>
              </div>

              <div className="space-y-2 mt-2">
                {customization.predefinedQuestions.map((question, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded group"
                  >
                    <span className="flex-grow">{question}</span>
                    <button
                      
                      onClick={() => handlePredefinedQuestionDelete(index)}
                      className="text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-4 mt-6">
              <Label>Response Templates</Label>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Input
                    value={newTrigger}
                    onChange={(e) => setNewTrigger(e.target.value)}
                    placeholder="Trigger phrase (e.g., 'pricing')"
                    className="flex-grow"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <Textarea
                    value={newResponse}
                    onChange={(e) => setNewResponse(e.target.value)}
                    placeholder="Bot response when trigger is detected"
                    className="flex-grow"
                    rows={2}
                  />
                  <Button  onClick={handleResponseTemplateAdd} type="button" className="h-full text-white">
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div className="space-y-2 mt-2">
                {customization.responseTemplates.map((template, index) => (
                  <div
                    key={index}
                    className="p-3 bg-gray-50 rounded group"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium">Trigger: "{template.trigger}"</span>
                      <button
                        onClick={() => handleResponseTemplateDelete(index)}
                        className="text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="text-sm text-gray-600">Response: "{template.response}"</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};