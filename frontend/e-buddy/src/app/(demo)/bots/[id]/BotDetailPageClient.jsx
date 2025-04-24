'use client';

import { useState,useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import BotFileManager from '@/components/chatbot/BotFileManager';
import { ContentLayout } from '@/components/admin-panel/content-layout';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  UserCircle,
  MessageSquare,
  Users,
  Settings,
  TrendingUp,
  Clock,
  CheckCircle2,
  Plus,
  X,
  FileText,
  Loader2
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

import { CustomizationForm } from '@/components/chatbot/CustomizationForm';
import { ChatPreview } from '@/components/chatbot/ChatPreview';
import { ChatTrigger } from '@/components/chatbot/ChatTrigger';
import { useToast } from '@/hooks/use-toast';
import { botAPI } from '@/services/api';

// Utility functions for mapping API values to expected enums
function mapChatBubbleStyle(style) {
  if (!style) return "rounded";
  switch (style.toLowerCase()) {
    case "bubble": return "bubble";
    case "sharp": return "sharp";
    default: return "rounded";
  }
}

function mapFontStyle(style) {
  if (!style) return "default";
  switch (style.toLowerCase()) {
    case "modern": return "modern";
    case "classic": return "classic";
    case "playful": return "playful";
    default: return "default";
  }
}


function mapPosition(position) {
  if (!position) return "right";
  return position.toLowerCase() === "left" ? "left" : "right";
}
// Transform API data to match the expected Bot structure
function transformApiBot(apiBot) {
  return {
    id: apiBot._id, // Ensure type consistency if necessary (e.g., parseInt(apiBot._id))
    name: apiBot.name,
    model: apiBot.ai_model_name,
    createdAt: apiBot.created_at || new Date().toISOString().split('T')[0],
    description: apiBot.description,
    stats: {
      conversations: apiBot.stats?.conversations || 0,
      leadGeneration: apiBot.stats?.leadGeneration || apiBot.stats?.leads || 0,
      conversionRate: apiBot.stats?.conversionRate || apiBot.stats?.conversion_rate || 0,
      avgResponseTime: apiBot.stats?.avgResponseTime || apiBot.stats?.avg_response_time || 'N/A',
      customerSatisfaction: apiBot.stats?.customerSatisfaction || apiBot.stats?.satisfaction || 0,
      activeUsers: apiBot.stats?.activeUsers || apiBot.stats?.active_users || 0,
    },
    performance: apiBot.performance || [], // Use performance data if available, else empty array
    customization: {
      name: apiBot.customization?.name ?? apiBot.name,
      avatarUrl: apiBot.customization?.avatarUrl ?? apiBot.avatar_url,
      primaryColor: apiBot.customization?.primaryColor ?? apiBot.primary_color ?? "#6366f1",
      secondaryColor: apiBot.customization?.secondaryColor ?? apiBot.secondary_color ?? "#f9fafb",
      chatBubbleStyle: mapChatBubbleStyle(
        apiBot.customization?.chatBubbleStyle ?? apiBot.chat_bubble_style
      ),
      welcomeMessage:
        apiBot.customization?.welcomeMessage ?? apiBot.welcome_message ?? apiBot.initial_message,
      font: mapFontStyle(apiBot.customization?.font ?? apiBot.font_style),
      position: mapPosition(apiBot.customization?.position ?? apiBot.position),
      predefinedQuestions: apiBot.customization?.predefinedQuestions ?? apiBot.predefined_questions ?? [],
      responseTemplates: apiBot.customization?.responseTemplates ?? apiBot.response_templates ?? []
    }
  };
}


import PropTypes from 'prop-types';

BotDetailPageClient.propTypes = {
  id: PropTypes.any.isRequired,
  fallbackBot: PropTypes.any.isRequired,
};

export default function BotDetailPageClient({ id, fallbackBot }) {
  const [currentBot, setCurrentBot] = useState(fallbackBot)
  const [customization, setCustomization] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const { toast } = useToast();

  // State to hold dummy custom fields for lead generation.
  const [welcomeMessage, setWelcomeMessage] = useState("Welcome! Please provide your information to get started.");
  const [formLayout, setFormLayout] = useState("standard");
  const [customFields, setCustomFields] = useState([]);
  const [newFieldName, setNewFieldName] = useState("");
  const [newFieldType, setNewFieldType] = useState("text");
  const [loading, setLoading] = useState(true);
  const [error,setError] =  useState(null);


  // Fetch bot data from API
  useEffect(() => {
    async function fetchBotData() {
      // Always show loading state when fetching data
      setLoading(true);
      
      try {
        const response = await botAPI.getBot(id);
        
        if (response.data.data) {
          const bot = transformApiBot(response.data.data);
          setCurrentBot(bot);
          setError(null); // Clear any errors if successful
        } else {
          setError("Bot not found");
          // Keep fallback data if available
          if (!fallbackBot) {
            setCurrentBot(null);
          }
        }
      } catch (err) {
        console.error("Error fetching bot:", err);
        setError("Failed to load bot details. Using fallback data if available.");
        // Keep fallback data if available
        if (!fallbackBot) {
          setCurrentBot(null);
        }
      } finally {
        setLoading(false);
      }
    }

    // Only fetch if we have an ID
    if (id) {
      fetchBotData();
    } else {
      setError("No bot ID provided");
      setLoading(false);
    }
  }, [id, fallbackBot]);


  useEffect(() => {
    if (currentBot) {
      setCustomization(currentBot.customization);
    }
  }, [currentBot]);

  // FIX: First check loading state
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
        <p className="text-gray-500">Loading bot details...</p>
      </div>
    );
  }

  // Then check for error state when there's no bot
  if ((error && !currentBot) || (!currentBot && !loading)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Bot not found</h2>
          <p className="text-gray-600 mb-4">We couldn't find the bot you're looking for.</p>
          <Link href="/bots/my-bots" className="text-blue-600 hover:underline">
            Back to My Bots
          </Link>
        </div>
      </div>
    );
  }

  // Finally check if we need to wait for customization
  if (!customization && currentBot) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
        <p className="text-gray-500">Preparing bot customization...</p>
      </div>
    );
  }




  const handleCustomizationChange = (newCustomization) => {
    setCustomization(newCustomization);
  };

  const handleSaveChanges = () => {
    // In a real application, this would be a API call to save the changes
    // For now, we'll just simulate it with a toast message
    setCurrentBot({
      ...currentBot,
      customization
    });
    
    toast({
      title: "Changes saved successfully",
      description: "Your chatbot customization has been updated.",
      duration: 3000,
      className: "animate-slide-in-from-right", // custom class added here
    });
    
  };

  const addCustomField = () => {
    if (newFieldName.trim()) {
      setCustomFields([
        ...customFields,
        { name: newFieldName, type: newFieldType }
      ]);
      setNewFieldName("");
    }
  };

  const deleteCustomField = (indexToDelete) => {
    setCustomFields(customFields.filter((_, index) => index !== indexToDelete));
  };

  // Function to update welcome message
  const handleWelcomeMessageUpdate = (newMessage) => {
    setWelcomeMessage(newMessage);
  };

  // Function to update form layout
  const handleFormLayoutUpdate = (newLayout) => {
    setFormLayout(newLayout);
  };

  // Show loading state first
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
        <p className="text-gray-500">Loading bot details...</p>
      </div>
    );
  }

  // Only show error if we have no bot data at all
  if (error && !bot) {
    return (
      <div className="p-6 text-center">
        <div className="p-4 border border-red-300 bg-red-50 text-red-700 rounded-md">
          {error}
        </div>
      </div>
    );
  }

  return (
    <ContentLayout title={currentBot.name}>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link href="/">Home</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link href="/dashboard">Dashboard</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link href="/bots/viewbots">My Bots</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>{currentBot.name}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      


      <div className="mt-6 space-y-6">
        {/* Hero Card */}
        <Card className="shadow-lg border border-gray-200 rounded-lg overflow-hidden bg-gradient-to-r from-blue-500 to-purple-600">
          <CardHeader className="relative h-64">
            <div className="absolute inset-0 bg-black bg-opacity-40 z-10" />
            <Image 
              src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop"
              alt={`${currentBot.name} Hero`} 
              fill
              className="object-cover" 
            />
            <div className="relative z-20 flex items-center space-x-4">
              <div className="bg-white rounded-full p-3 shadow-lg">
                <UserCircle className="w-12 h-12 text-blue-600" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-white">{currentBot.name}</h1>
                <p className="text-gray-200 mt-2">Powered by {currentBot.model}</p>
              </div>
            </div>
          </CardHeader>
        </Card>

         {/* Quick Stats */}
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-600 font-medium">Conversion Rate</p>
                  <h3 className="text-2xl font-bold text-green-700">
                    {currentBot.stats.conversionRate}%
                  </h3>
                </div>
                <TrendingUp className="w-8 h-8 text-green-500" />
              </div>
              <Progress value={currentBot.stats.conversionRate} className="mt-4" />
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-600 font-medium">Active Users</p>
                  <h3 className="text-2xl font-bold text-blue-700">
                    {currentBot.stats.activeUsers}
                  </h3>
                </div>
                <Users className="w-8 h-8 text-blue-500" />
              </div>
              <Progress value={75} className="mt-4" />
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-600 font-medium">Response Time</p>
                  <h3 className="text-2xl font-bold text-purple-700">
                    {currentBot.stats.avgResponseTime}
                  </h3>
                </div>
                <Clock className="w-8 h-8 text-purple-500" />
              </div>
              <Progress value={90} className="mt-4" />
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-orange-600 font-medium">Satisfaction</p>
                  <h3 className="text-2xl font-bold text-orange-700">
                    {currentBot.stats.customerSatisfaction}%
                  </h3>
                </div>
                <CheckCircle2 className="w-8 h-8 text-orange-500" />
              </div>
              <Progress value={currentBot.stats.customerSatisfaction} className="mt-4" />
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="performance" className="w-full">
        <TabsList className="flex flex-wrap justify-between gap-2 rounded-lg bg-gray-100 p-1">
              <TabsTrigger value="performance" className="flex-1 text-center data-[state=active]:bg-white">
                Performance
              </TabsTrigger>
              <TabsTrigger value="customization" className="flex-1 text-center data-[state=active]:bg-white">
                Customization
              </TabsTrigger>
              <TabsTrigger value="files" className="flex-1 text-center data-[state=active]:bg-white">
                Files
              </TabsTrigger>
              <TabsTrigger value="leads" className="flex-1 text-center data-[state=active]:bg-white">
                Lead Generation
              </TabsTrigger>
              <TabsTrigger value="settings" className="flex-1 text-center data-[state=active]:bg-white">
                Settings
              </TabsTrigger>
            </TabsList>

          <TabsContent value="performance" className="mt-6">
            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-4">Performance Analytics</h3>
                <div className="h-[400px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={currentBot.performance}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="conversations" stroke="#8884d8" />
                      <Line type="monotone" dataKey="leads" stroke="#82ca9d" />
                      <Line type="monotone" dataKey="sales" stroke="#ffc658" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>


        <TabsContent value="customization" className="mt-6">
            <div className="flex space-x-3">
                  <Button 
                    variant="outline"
                    onClick={() => setShowPreview(!showPreview)}
                  >
                    {showPreview ? 'Hide Preview' : 'Show Preview'}
                  </Button>
                  <Button onClick={handleSaveChanges} className="text-white" >Save Changes</Button>
                
            </div>
            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-4">Bot Customization</h3>
                <CustomizationForm 
                  customization={customization}
                  onChange={handleCustomizationChange}
                />
              </CardContent>
            </Card>
          </TabsContent>

           {/* NEW FILES TAB */}
           <TabsContent value="files" className="mt-6">
            <div className="mb-4">
              <h3 className="text-xl font-semibold mb-2">Bot Files and Training Data</h3>
              <p className="text-gray-600 mb-4">
                Upload files to train your bot with domain-specific knowledge. Supported file types include PDFs, 
                Office documents, text files, and images.
              </p>
            </div>

            <BotFileManager botId={currentBot.id} />

            <Card className="mt-6">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-blue-50 text-blue-600 rounded-full">
                    <FileText className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="text-lg font-medium mb-1">Using Files with Your Bot</h4>
                    <p className="text-gray-600 mb-3">
                      Files uploaded to your bot will be processed and indexed for your bot to reference 
                      during conversations. This helps your bot provide more accurate and domain-specific responses.
                    </p>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-start gap-2">
                        <span className="font-medium">•</span>
                        <p>PDF documents with product specifications will help your bot answer detailed product questions</p>
                      </div>
                      <div className="flex items-start gap-2">
                        <span className="font-medium">•</span>
                        <p>Support documentation helps your bot troubleshoot customer issues</p>
                      </div>
                      <div className="flex items-start gap-2">
                        <span className="font-medium">•</span>
                        <p>Training materials help keep your bot's knowledge up-to-date</p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>


          <TabsContent value="leads" className="mt-6">
            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-4">Lead Collection Configuration</h3>
                <div className="space-y-6">
                  {/* Required Fields Section */}
                  <Card className="bg-white">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-medium text-lg">Required Information</h4>
                        <Settings className="w-6 h-6 text-gray-400" />
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="flex items-start space-x-3">
                          <input type="checkbox" className="mt-1" checked readOnly />
                          <div>
                            <p className="font-medium">Name</p>
                            <p className="text-sm text-gray-600">Collect user's full name</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <input type="checkbox" className="mt-1" checked readOnly />
                          <div>
                            <p className="font-medium">Email</p>
                            <p className="text-sm text-gray-600">Primary contact email</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <input type="checkbox" className="mt-1" />
                          <div>
                            <p className="font-medium">Phone Number</p>
                            <p className="text-sm text-gray-600">Contact phone number</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <input type="checkbox" className="mt-1" />
                          <div>
                            <p className="font-medium">Company</p>
                            <p className="text-sm text-gray-600">Business or organization name</p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Form Customization */}
                  <Card className="bg-white">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-medium text-lg">Form Customization</h4>
                        <MessageSquare className="w-6 h-6 text-gray-400" />
                      </div>
                      <div className="space-y-4">
                        {/* Welcome Message Dialog */}
                        <Dialog>
                          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                              <p className="font-medium">Welcome Message</p>
                              <p className="text-sm text-gray-600">Current: {welcomeMessage}</p>
                            </div>
                            <DialogTrigger asChild>
                              <Button variant="outline">Edit</Button>
                            </DialogTrigger>
                          </div>
                          <DialogContent className="sm:max-w-[425px] bg-blue-50">
                            <DialogHeader>
                              <DialogTitle>Edit Welcome Message</DialogTitle>
                              <DialogDescription>
                                Update the message that users see before starting the chat.
                              </DialogDescription>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                              <div className="grid gap-2">
                                <Label htmlFor="welcome-message">Message</Label>
                                <Textarea
                                  id="welcome-message"
                                  defaultValue={welcomeMessage}
                                  onChange={(e) => handleWelcomeMessageUpdate(e.target.value)}
                                />
                              </div>
                            </div>
                            <DialogFooter>
                              <Button type="submit">Save changes</Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>

                        {/* Form Layout Dialog */}
                        <Dialog>
                          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                              <p className="font-medium">Form Layout</p>
                              <p className="text-sm text-gray-600">Current: {formLayout}</p>
                            </div>
                            <DialogTrigger asChild>
                              <Button variant="outline">Customize</Button>
                            </DialogTrigger>
                          </div>
                          <DialogContent className="sm:max-w-[425px] bg-blue-50">
                            <DialogHeader>
                              <DialogTitle>Customize Form Layout</DialogTitle>
                              <DialogDescription>
                                Choose how you want to arrange your form fields.
                              </DialogDescription>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                              <div className="grid gap-2">
                                <Label>Layout Style</Label>
                                <select
                                  className="w-full p-2 border rounded"
                                  value={formLayout}
                                  onChange={(e) => handleFormLayoutUpdate(e.target.value)}
                                >
                                  <option value="standard">Standard</option>
                                  <option value="compact">Compact</option>
                                  <option value="spacious">Spacious</option>
                                </select>
                              </div>
                            </div>
                            <DialogFooter>
                              <Button type="submit">Save changes</Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>


                        {/* Custom Fields Modal */}
                        <Dialog>
                          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                              <p className="font-medium">Custom Fields</p>
                              <p className="text-sm text-gray-600">
                                {customFields.length} custom field{customFields.length !== 1 && "s"} added
                              </p>
                            </div>
                            <DialogTrigger asChild>
                              <Button variant="outline">Configure</Button>
                            </DialogTrigger>
                          </div>
                          <DialogContent className="sm:max-w-[425px] bg-blue-50">
                            <DialogHeader>
                              <DialogTitle>Configure Custom Fields</DialogTitle>
                              <DialogDescription>
                                Add additional fields to collect more information.
                              </DialogDescription>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                              <div className="grid gap-2">
                                <Label htmlFor="field-name">Field Name</Label>
                                <Input
                                  id="field-name"
                                  value={newFieldName}
                                  onChange={(e) => setNewFieldName(e.target.value)}
                                  placeholder="Enter field name"
                                />
                              </div>
                              <div className="grid gap-2">
                                <Label htmlFor="field-type">Field Type</Label>
                                <select
                                  id="field-type"
                                  className="w-full p-2 border rounded"
                                  value={newFieldType}
                                  onChange={(e) => setNewFieldType(e.target.value)}
                                >
                                  <option value="text">Text</option>
                                  <option value="number">Number</option>
                                  <option value="email">Email</option>
                                  <option value="tel">Phone</option>
                                  <option value="date">Date</option>
                                </select>
                              </div>
                              <Button onClick={addCustomField} className="w-full">
                                <Plus className="w-4 h-4 mr-2" />
                                Add Field
                              </Button>
                              {customFields.length > 0 && (
                                <div className="mt-4">
                                  <Label>Current Custom Fields</Label>
                                  <div className="mt-2 space-y-2">
                                    {customFields.map((field, index) => (
                                      <div
                                        key={field.id || `${field.name}-${field.type}`} // Use a unique identifier instead
                                        className="flex items-center justify-between p-2 bg-gray-50 rounded"
                                      >
                                        <span>{field.name} ({field.type})</span>
                                        <button
                                          onClick={() => deleteCustomField(index)}
                                          className="text-red-500 hover:text-red-700"
                                        >
                                          <X className="w-4 h-4" />
                                        </button>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                            <DialogFooter>
                              <Button type="submit">Save changes</Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Data Processing Section */}
                  <Card>
                    <CardHeader>
                      <h4 className="text-lg font-medium">Integrations</h4>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Card className="bg-gray-50">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-center">
                              <div className="flex items-center space-x-3">
                                <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                  <rect width="24" height="24" rx="4" fill="#FF5A00" />
                                  <path d="M18 7.2H6V16.8H18V7.2Z" fill="white" />
                                </svg>
                                <div>
                                  <p className="font-medium">HubSpot</p>
                                  <p className="text-sm text-gray-600">CRM Integration</p>
                                </div>
                              </div>
                              <Button variant="outline" size="sm">Connect</Button>
                            </div>
                          </CardContent>
                        </Card>
                        
                        <Card className="bg-gray-50">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-center">
                              <div className="flex items-center space-x-3">
                                <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                  <rect width="24" height="24" rx="4" fill="#00A1E0" />
                                  <path d="M12 4L6 8V16L12 20L18 16V8L12 4Z" fill="white" />
                                </svg>
                                <div>
                                  <p className="font-medium">Salesforce</p>
                                  <p className="text-sm text-gray-600">CRM Integration</p>
                                </div>
                              </div>
                              <Button variant="outline" size="sm">Connect</Button>
                            </div>
                          </CardContent>
                        </Card>
                        
                        <Card className="bg-gray-50">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-center">
                              <div className="flex items-center space-x-3">
                                <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                  <rect width="24" height="24" rx="4" fill="#36B37E" />
                                  <path d="M6 12L10 16L18 8" stroke="white" strokeWidth="2" />
                                </svg>
                                <div>
                                  <p className="font-medium">Mailchimp</p>
                                  <p className="text-sm text-gray-600">Email Marketing</p>
                                </div>
                              </div>
                              <Button variant="outline" size="sm">Connect</Button>
                            </div>
                          </CardContent>
                        </Card>
                        
                        <Card className="bg-gray-50">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-center">
                              <div className="flex items-center space-x-3">
                                <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                  <rect width="24" height="24" rx="4" fill="#4353FF" />
                                  <path d="M6 8H18V16H6V8Z" fill="white" />
                                </svg>
                                <div>
                                  <p className="font-medium">Zapier</p>
                                  <p className="text-sm text-gray-600">Workflow Automation</p>
                                </div>
                              </div>
                              <Button variant="outline" size="sm">Connect</Button>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="mt-6">
            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-4">Bot Settings</h3>
                <div className="space-y-6">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium">Operating Hours</h4>
                      <p className="text-sm text-gray-600">Set when your bot is active</p>
                    </div>
                    <Button variant="outline" size="sm">
                      <Settings className="w-4 h-4 mr-2" /> Configure
                    </Button>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium">Language Settings</h4>
                      <p className="text-sm text-gray-600">Configure bot languages</p>
                    </div>
                    <Button variant="outline" size="sm">
                      <Settings className="w-4 h-4 mr-2" /> Configure
                    </Button>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium">Integration Settings</h4>
                      <p className="text-sm text-gray-600">Manage third-party integrations</p>
                    </div>
                    <Button variant="outline" size="sm">
                      <Settings className="w-4 h-4 mr-2" /> Configure
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Chat Preview */}
        {showPreview ? (
          <ChatPreview 
            customization={customization} 
            onClose={() => setShowPreview(false)} 
          />
        ) : (
          <ChatTrigger 
            customization={customization} 
            onClick={() => setShowPreview(true)} 
          />
        )}
      </div>

    </ContentLayout>
  );
}
