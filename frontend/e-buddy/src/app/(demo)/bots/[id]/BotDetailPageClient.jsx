'use client';

import { useState } from 'react';
import { useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
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
import { toast } from '@/hooks/use-toast';
import { BotCustomization } from '@/types/chatbot';
import { dummyBots } from '@/data/botData';

export default function BotDetailPageClient({bot}) {
  // const { id } = useParams();
  // const [bot, setBot] = useState(dummyBots.find(b => b.id.toString() === id));
  // const [customization, setCustomization] = useState<BotCustomization | null>(null);
  const [currentBot, setCurrentBot] = useState(bot)
  const [customization, setCustomization] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  // State to hold dummy custom fields for lead generation.
  const [welcomeMessage, setWelcomeMessage] = useState("Welcome! Please provide your information to get started.");
  const [formLayout, setFormLayout] = useState("standard");
  const [customFields, setCustomFields] = useState([]);
  const [newFieldName, setNewFieldName] = useState("");
  const [newFieldType, setNewFieldType] = useState("text");

  useEffect(() => {
    if (!currentBot) return;
      setCustomization(currentBot.customization);
    }, [currentBot]);

    if (!currentBot || !customization) {
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
          <TabsList className="grid w-full grid-cols-4 rounded-lg bg-gray-100 p-1">
            <TabsTrigger value="performance" className="data-[state=active]:bg-white">
              Performance
            </TabsTrigger>
            <TabsTrigger value="customization" className="data-[state=active]:bg-white">
              Customization
            </TabsTrigger>
            <TabsTrigger value="leads" className="data-[state=active]:bg-white">
              Lead Generation
            </TabsTrigger>
            <TabsTrigger value="settings" className="data-[state=active]:bg-white">
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

          {/* <TabsContent value="customization" className="mt-6">
            <Card>
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-4">Bot Customization</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-medium">Conversation Flow</h4>
                    <div className="space-y-2">
                      <Link href="#" className="block text-blue-600 hover:underline">
                        • Edit Welcome Message
                      </Link>
                      <Link href="#" className="block text-blue-600 hover:underline">
                        • Customize Response Templates
                      </Link>
                      <Link href="#" className="block text-blue-600 hover:underline">
                        • Configure Product Recommendations
                      </Link>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-medium">Appearance</h4>
                    <div className="space-y-2">
                      <Link href="#" className="block text-blue-600 hover:underline">
                        • Change Bot Avatar
                      </Link>
                      <Link href="#" className="block text-blue-600 hover:underline">
                        • Modify Chat Window Style
                      </Link>
                      <Link href="#" className="block text-blue-600 hover:underline">
                        • Update Color Scheme
                      </Link>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent> */}

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
                                        key={index}
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
