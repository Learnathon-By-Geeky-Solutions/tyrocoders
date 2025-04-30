'use client';

import { useState } from 'react';
import { useEffect } from 'react';
import { useParams } from 'next/navigation';
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
  ShoppingCart,
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
import { BotCustomization } from '@/types/chatbot';
import { dummyBots } from '@/data/botData';
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

const dummyPerformance = [
  { date: "2025-04-24", conversations: 120, leads: 20, sales: 5 },
  { date: "2025-04-25", conversations: 150, leads: 25, sales: 7 },
  { date: "2025-04-26", conversations: 170, leads: 30, sales: 6 },
  { date: "2025-04-27", conversations: 160, leads: 28, sales: 8 },
  { date: "2025-04-28", conversations: 180, leads: 35, sales: 10 },
  { date: "2025-04-29", conversations: 200, leads: 40, sales: 12 },
  { date: "2025-04-30", conversations: 190, leads: 38, sales: 11 },
];


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
    createdAt: apiBot.created_at || new Date().toISOString().split("T")[0],
    description: apiBot.description,
    stats: {
      conversations: apiBot.stats?.conversations || 0,
      leadGeneration: apiBot.stats?.leadGeneration || apiBot.stats?.leads || 0,
      conversionRate:
        apiBot.stats?.conversionRate || apiBot.stats?.conversion_rate || 0,
      avgResponseTime:
        apiBot.stats?.avgResponseTime ||
        apiBot.stats?.avg_response_time ||
        "N/A",
      customerSatisfaction:
        apiBot.stats?.customerSatisfaction || apiBot.stats?.satisfaction || 0,
      activeUsers: apiBot.stats?.activeUsers || apiBot.stats?.active_users || 0,
    },
    performance: apiBot.performance || dummyPerformance, // Use performance data if available, else empty array
    customization: {
      name: (apiBot.customization && apiBot.customization.name) || apiBot.name,
      avatarUrl:
        (apiBot.customization && apiBot.customization.avatarUrl) ||
        apiBot.avatar_url,
      primaryColor:
        (apiBot.customization && apiBot.customization.primaryColor) ||
        apiBot.primary_color ||
        "#6366f1",
      secondaryColor:
        (apiBot.customization && apiBot.customization.secondaryColor) ||
        apiBot.secondary_color ||
        "#f9fafb",
      chatBubbleStyle: mapChatBubbleStyle(
        (apiBot.customization && apiBot.customization.chatBubbleStyle) ||
          apiBot.chat_bubble_style
      ),
      welcomeMessage:
        (apiBot.customization && apiBot.customization.welcomeMessage) ||
        apiBot.welcome_message ||
        apiBot.initial_message,
      font: mapFontStyle(
        (apiBot.customization && apiBot.customization.font) || apiBot.font_style
      ),
      position: mapPosition(
        (apiBot.customization && apiBot.customization.position) ||
          apiBot.position
      ),
      predefinedQuestions:
        (apiBot.customization && apiBot.customization.predefinedQuestions) ||
        apiBot.predefined_questions ||
        [],
      responseTemplates:
        (apiBot.customization && apiBot.customization.responseTemplates) ||
        apiBot.response_templates ||
        [],
    },
  };
}


export default function BotDetailPageClient({ id, fallbackBot }) {

  // const { id } = useParams();
  // const [bot, setBot] = useState(dummyBots.find(b => b.id.toString() === id));
  // const [customization, setCustomization] = useState<BotCustomization | null>(null);
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
              <Link href="/bots/view">Bots</Link>
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

        {/* Main Content Tabs */}
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="flex flex-wrap justify-between gap-2 rounded-lg bg-gray-100 p-1">
            <TabsTrigger
              value="overview"
              className="flex-1 text-center data-[state=active]:bg-white"
            >
              Overview
            </TabsTrigger>
            <TabsTrigger
              value="performance"
              className="flex-1 text-center data-[state=active]:bg-white"
            >
              Performance
            </TabsTrigger>
            <TabsTrigger
              value="customization"
              className="flex-1 text-center data-[state=active]:bg-white"
            >
              Customization
            </TabsTrigger>
            <TabsTrigger
              value="files"
              className="flex-1 text-center data-[state=active]:bg-white"
            >
              Files
            </TabsTrigger>
            <TabsTrigger
              value="leads"
              className="flex-1 text-center data-[state=active]:bg-white"
            >
              Lead Generation
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6">
            <div className="max-w-4xl mx-auto bg-gradient-to-br from-white to-gray-50 shadow-xl rounded-2xl p-8 border border-gray-100">
              {/* Header Section with chatbot icon and name inline */}
              <div className="mb-8 text-center">
                <div className="flex flex-col items-center">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-orange-100 rounded-full">
                      <div className="h-12 w-12 rounded-full bg-accent flex items-center justify-center">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-6 w-6 text-white"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <rect x="3" y="11" width="18" height="10" rx="2" />
                          <circle cx="12" cy="5" r="2" />
                          <path d="M12 7v4" />
                          <line x1="8" y1="16" x2="8" y2="16" />
                          <line x1="16" y1="16" x2="16" y2="16" />
                          <path d="M9 20l3 2 3-2" />
                        </svg>
                      </div>
                    </div>
                    <h1 className="text-4xl font-bold text-gray-800">
                      {currentBot.name}
                    </h1>
                  </div>

                  {/* Model and Created On in smaller text */}
                  <div className="mt-2 flex flex-col sm:flex-row items-center justify-center space-y-1 sm:space-y-0 sm:space-x-4 text-sm text-gray-500">
                    <div className="flex items-center space-x-1">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-4 w-4 text-blue-500"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M14 13.5H9.5L4.5 18.5H19.5L14.5 13.5" />
                        <path d="M5 5.5h14l1.5 3-8.5 9-8.5-9z" />
                        <path d="M12 7.5v5" />
                      </svg>
                      <span>{currentBot.model}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-4 w-4 text-green-500"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <rect
                          x="3"
                          y="4"
                          width="18"
                          height="18"
                          rx="2"
                          ry="2"
                        />
                        <line x1="16" y1="2" x2="16" y2="6" />
                        <line x1="8" y1="2" x2="8" y2="6" />
                        <line x1="3" y1="10" x2="21" y2="10" />
                      </svg>
                      <span>Created on {currentBot.createdAt}</span>
                    </div>
                  </div>

                  <p className="mt-4 text-lg text-gray-600 max-w-lg mx-auto">
                    {currentBot.description}
                  </p>
                  <div className="mt-4 h-1 w-24 mx-auto bg-accent rounded-full"></div>
                </div>
              </div>

              {/* KEEP everything else exactly the same below */}
              {/* Additional Info Cards - Model and Creation Date */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
                {/* removed the previous "model" and "created on" cards */}
              </div>

              {/* Enhanced Stats Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 transform hover:-translate-y-1 flex flex-col items-center">
                  <div className="rounded-full p-3 bg-purple-100 mb-3">
                    <svg
                      key="messages"
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-6 w-6 text-purple-600"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-500 text-center">
                    Conversations
                  </p>
                  <p className="mt-2 text-3xl font-bold text-gray-800">
                    <span className="text-purple-500">
                      {currentBot.stats.conversations}
                    </span>
                  </p>
                </div>

                {/* Lead Generation */}
                <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 transform hover:-translate-y-1 flex flex-col items-center">
                  <div className="rounded-full p-3 bg-orange-100 mb-3">
                    <svg
                      key="users"
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-6 w-6 text-orange-600"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                      <circle cx="9" cy="7" r="4"></circle>
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                      <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-500 text-center">
                    Lead Generation
                  </p>
                  <p className="mt-2 text-3xl font-bold text-gray-800">
                    <span className="text-orange-500">
                      {currentBot.stats.leadGeneration}
                    </span>
                  </p>
                </div>

                {/* Active Users */}
                <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 transform hover:-translate-y-1 flex flex-col items-center">
                  <div className="rounded-full p-3 bg-blue-100 mb-3">
                    <svg
                      key="activeusers"
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-6 w-6 text-blue-600"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-500 text-center">
                    Active Users
                  </p>
                  <p className="mt-2 text-3xl font-bold text-gray-800">
                    <span className="text-blue-500">
                      {currentBot.stats.activeUsers}
                    </span>
                  </p>
                </div>

                {/* Conversion Rate */}
                <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 transform hover:-translate-y-1 flex flex-col items-center">
                  <div className="rounded-full p-3 bg-green-100 mb-3">
                    <svg
                      key="accuracy"
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-6 w-6 text-green-600"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                      <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-500 text-center">
                    Conversion Rate
                  </p>
                  <p className="mt-2 text-3xl font-bold text-gray-800">
                    <span className="text-green-500">
                      {currentBot.stats.conversionRate}%
                    </span>
                  </p>
                </div>
              </div>

              {/* Footer */}
              <div className="mt-8 pt-4 border-t border-gray-100 text-center">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 mr-1"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Last updated today
                </span>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="performance" className="mt-6">
            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-4">
                  Performance Analytics
                </h3>
                <div className="h-[400px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={currentBot.performance}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="conversations"
                        name="Conversations"
                        stroke="#8884d8"
                        dot={{ r: 3 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="leads"
                        name="Leads"
                        stroke="#82ca9d"
                        dot={{ r: 3 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="sales"
                        name="Sales"
                        stroke="#ffc658"
                        dot={{ r: 3 }}
                      />
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
                {showPreview ? "Hide Preview" : "Show Preview"}
              </Button>
              <Button onClick={handleSaveChanges} className="text-white">
                Save Changes
              </Button>
            </div>
            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-4">
                  Bot Customization
                </h3>
                <CustomizationForm
                  customization={customization}
                  onChange={handleCustomizationChange}
                />
              </CardContent>
            </Card>
          </TabsContent>

          {/* NEW FILES TAB */}
          <TabsContent value="files" className="mt-6">
            <BotFileManager botId={currentBot.id} />
          </TabsContent>

          <TabsContent value="leads" className="mt-6">
            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-4">
                  Lead Collection Configuration
                </h3>
                <div className="space-y-6">
                  {/* Required Fields Section */}
                  <Card className="bg-white">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-medium text-lg">
                          Required Information
                        </h4>
                        <Settings className="w-6 h-6 text-gray-400" />
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="flex items-start space-x-3">
                          <input
                            type="checkbox"
                            className="mt-1"
                            checked
                            readOnly
                          />
                          <div>
                            <p className="font-medium">Name</p>
                            <p className="text-sm text-gray-600">
                              Collect user's full name
                            </p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <input
                            type="checkbox"
                            className="mt-1"
                            checked
                            readOnly
                          />
                          <div>
                            <p className="font-medium">Email</p>
                            <p className="text-sm text-gray-600">
                              Primary contact email
                            </p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <input type="checkbox" className="mt-1" />
                          <div>
                            <p className="font-medium">Phone Number</p>
                            <p className="text-sm text-gray-600">
                              Contact phone number
                            </p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <input type="checkbox" className="mt-1" />
                          <div>
                            <p className="font-medium">Company</p>
                            <p className="text-sm text-gray-600">
                              Business or organization name
                            </p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Form Customization */}
                  <Card className="bg-white">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-medium text-lg">
                          Form Customization
                        </h4>
                        <MessageSquare className="w-6 h-6 text-gray-400" />
                      </div>
                      <div className="space-y-4">
                        {/* Welcome Message Dialog */}
                        <Dialog>
                          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                              <p className="font-medium">Welcome Message</p>
                              <p className="text-sm text-gray-600">
                                Current: {welcomeMessage}
                              </p>
                            </div>
                            <DialogTrigger asChild>
                              <Button variant="outline">Edit</Button>
                            </DialogTrigger>
                          </div>
                          <DialogContent className="sm:max-w-[425px] bg-blue-50">
                            <DialogHeader>
                              <DialogTitle>Edit Welcome Message</DialogTitle>
                              <DialogDescription>
                                Update the message that users see before
                                starting the chat.
                              </DialogDescription>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                              <div className="grid gap-2">
                                <Label htmlFor="welcome-message">Message</Label>
                                <Textarea
                                  id="welcome-message"
                                  defaultValue={welcomeMessage}
                                  onChange={(e) =>
                                    handleWelcomeMessageUpdate(e.target.value)
                                  }
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
                              <p className="text-sm text-gray-600">
                                Current: {formLayout}
                              </p>
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
                                  onChange={(e) =>
                                    handleFormLayoutUpdate(e.target.value)
                                  }
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
                                {customFields.length} custom field
                                {customFields.length !== 1 && "s"} added
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
                                Add additional fields to collect more
                                information.
                              </DialogDescription>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                              <div className="grid gap-2">
                                <Label htmlFor="field-name">Field Name</Label>
                                <Input
                                  id="field-name"
                                  value={newFieldName}
                                  onChange={(e) =>
                                    setNewFieldName(e.target.value)
                                  }
                                  placeholder="Enter field name"
                                />
                              </div>
                              <div className="grid gap-2">
                                <Label htmlFor="field-type">Field Type</Label>
                                <select
                                  id="field-type"
                                  className="w-full p-2 border rounded"
                                  value={newFieldType}
                                  onChange={(e) =>
                                    setNewFieldType(e.target.value)
                                  }
                                >
                                  <option value="text">Text</option>
                                  <option value="number">Number</option>
                                  <option value="email">Email</option>
                                  <option value="tel">Phone</option>
                                  <option value="date">Date</option>
                                </select>
                              </div>
                              <Button
                                onClick={addCustomField}
                                className="w-full"
                              >
                                <Plus className="w-4 h-4 mr-2" />
                                Add Field
                              </Button>
                              {customFields.length > 0 && (
                                <div className="mt-4">
                                  <Label>Current Custom Fields</Label>
                                  <div className="mt-2 space-y-2">
                                    {customFields.map((field, index) => (
                                      <div
                                        key={index}
                                        className="flex items-center justify-between p-2 bg-gray-50 rounded"
                                      >
                                        <span>
                                          {field.name} ({field.type})
                                        </span>
                                        <button
                                          onClick={() =>
                                            deleteCustomField(index)
                                          }
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
                                <svg
                                  className="w-8 h-8"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  xmlns="http://www.w3.org/2000/svg"
                                >
                                  <rect
                                    width="24"
                                    height="24"
                                    rx="4"
                                    fill="#FF5A00"
                                  />
                                  <path
                                    d="M18 7.2H6V16.8H18V7.2Z"
                                    fill="white"
                                  />
                                </svg>
                                <div>
                                  <p className="font-medium">HubSpot</p>
                                  <p className="text-sm text-gray-600">
                                    CRM Integration
                                  </p>
                                </div>
                              </div>
                              <Button variant="outline" size="sm">
                                Connect
                              </Button>
                            </div>
                          </CardContent>
                        </Card>

                        <Card className="bg-gray-50">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-center">
                              <div className="flex items-center space-x-3">
                                <svg
                                  className="w-8 h-8"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  xmlns="http://www.w3.org/2000/svg"
                                >
                                  <rect
                                    width="24"
                                    height="24"
                                    rx="4"
                                    fill="#00A1E0"
                                  />
                                  <path
                                    d="M12 4L6 8V16L12 20L18 16V8L12 4Z"
                                    fill="white"
                                  />
                                </svg>
                                <div>
                                  <p className="font-medium">Salesforce</p>
                                  <p className="text-sm text-gray-600">
                                    CRM Integration
                                  </p>
                                </div>
                              </div>
                              <Button variant="outline" size="sm">
                                Connect
                              </Button>
                            </div>
                          </CardContent>
                        </Card>

                        <Card className="bg-gray-50">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-center">
                              <div className="flex items-center space-x-3">
                                <svg
                                  className="w-8 h-8"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  xmlns="http://www.w3.org/2000/svg"
                                >
                                  <rect
                                    width="24"
                                    height="24"
                                    rx="4"
                                    fill="#36B37E"
                                  />
                                  <path
                                    d="M6 12L10 16L18 8"
                                    stroke="white"
                                    strokeWidth="2"
                                  />
                                </svg>
                                <div>
                                  <p className="font-medium">Mailchimp</p>
                                  <p className="text-sm text-gray-600">
                                    Email Marketing
                                  </p>
                                </div>
                              </div>
                              <Button variant="outline" size="sm">
                                Connect
                              </Button>
                            </div>
                          </CardContent>
                        </Card>

                        <Card className="bg-gray-50">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-center">
                              <div className="flex items-center space-x-3">
                                <svg
                                  className="w-8 h-8"
                                  viewBox="0 0 24 24"
                                  fill="none"
                                  xmlns="http://www.w3.org/2000/svg"
                                >
                                  <rect
                                    width="24"
                                    height="24"
                                    rx="4"
                                    fill="#4353FF"
                                  />
                                  <path d="M6 8H18V16H6V8Z" fill="white" />
                                </svg>
                                <div>
                                  <p className="font-medium">Zapier</p>
                                  <p className="text-sm text-gray-600">
                                    Workflow Automation
                                  </p>
                                </div>
                              </div>
                              <Button variant="outline" size="sm">
                                Connect
                              </Button>
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
        </Tabs>

        {/* Chat Preview */}
        {showPreview ? (
          <ChatPreview
            customization={customization}
            onClose={() => setShowPreview(false)}
            chatbotId={currentBot.id}
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
