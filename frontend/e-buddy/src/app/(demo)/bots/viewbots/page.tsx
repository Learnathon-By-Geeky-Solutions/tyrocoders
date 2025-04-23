"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage, 
  BreadcrumbSeparator
} from "@/components/ui/breadcrumb";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowRight, MessageSquare, Star, Plus, Loader2 } from "lucide-react";
import { botAPI } from "@/services/api";
import { Bot } from "@/data/botData";

function mapChatBubbleStyle(style?: string): "rounded" | "sharp" | "bubble" {
  if (!style) return "rounded";
  switch (style.toLowerCase()) {
    case "bubble": return "bubble";
    case "sharp": return "sharp";
    default: return "rounded";
  }
}

function mapFontStyle(style?: string): "default" | "modern" | "classic" | "playful" {
  if (!style) return "default";
  switch (style.toLowerCase()) {
    case "modern": return "modern";
    case "classic": return "classic";
    case "playful": return "playful";
    default: return "default";
  }
}

function mapPosition(position?: string): "right" | "left" {
  if (!position) return "right";
  return position.toLowerCase() === "left" ? "left" : "right";
}

export default function MyBotsPage() {
  const [bots, setBots] = useState<Bot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchBots() {
      try {
        setLoading(true);
        const response = await botAPI.getAllBots();
        
        if (response.data?.data) {
          // Transform API data to match the expected Bot structure
          const transformedBots = response.data.data.map((apiBot: any) => {
            // Transform to match Bot structure using actual API data
            return {
              id: apiBot._id, // Create a numeric ID from MongoDB ID
              name: apiBot.name,
              model: apiBot.ai_model_name,
              createdAt: apiBot.created_at ?? new Date().toISOString().split('T')[0],
              description: apiBot.description,
              stats: {
                conversations: apiBot.stats?.conversations ?? 0,
                leadGeneration: apiBot.stats?.leads ?? 0,
                conversionRate: apiBot.stats?.conversion_rate ?? 0,
                avgResponseTime: apiBot.stats?.avg_response_time ?? 'N/A',
                customerSatisfaction: apiBot.stats?.satisfaction ?? 0,
                activeUsers: apiBot.stats?.active_users ?? 0,
              },
              performance: [], // We don't need this for the list view
              customization: {
                name: apiBot.name,
                avatarUrl: apiBot.avatar_url,
                primaryColor: apiBot.primary_color ?? "#6366f1",
                secondaryColor: apiBot.secondary_color ?? "#f9fafb",
                chatBubbleStyle: mapChatBubbleStyle(apiBot.chat_bubble_style),
                welcomeMessage: apiBot.welcome_message,
                font: mapFontStyle(apiBot.font_style),
                position: mapPosition(apiBot.position),
                predefinedQuestions: apiBot.predefined_questions ?? [],
                responseTemplates: apiBot.response_templates ?? []
              }
            };

          });
          
          setBots(transformedBots);
        } else {
          setError("Invalid response format");
        }
      } catch (err) {
        console.error("Error fetching bots:", err);
        setError("Failed to fetch bots. Please try again later.");
      } finally {
        setLoading(false);
      }
    }

    fetchBots();
  }, []);

  return (
    <ContentLayout title="My Bots">
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
            <BreadcrumbPage>My Bots</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Grid/Card View */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Your Chatbots</h2>
        <Button asChild variant="outline">
          <Link href="/create-bot">
            <Plus className="mr-2 h-4 w-4" /> Create New Bot
          </Link>
        </Button>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-500">Loading your bots...</span>
        </div>
      ) : error ? (
        <div className="p-4 border border-red-300 bg-red-50 text-red-700 rounded-md">
          {error}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {bots.length > 0 ? (
            bots.map((bot) => (
              <Card
                key={bot.id}
                className="overflow-hidden hover:shadow-lg transition-shadow"
              >
                <div
                  className="h-3"
                  style={{
                    backgroundColor: bot.customization?.primaryColor ?? "#6366f1"
                  }}
                />
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div
                        className="w-10 h-10 rounded-full flex items-center justify-center"
                        style={{
                          backgroundColor:
                            (bot.customization?.primaryColor ?? "#6366f1") + "20"
                        }}
                      >
                        <MessageSquare
                          className="h-5 w-5"
                          style={{
                            color: bot.customization?.primaryColor ?? "#6366f1"
                          }}
                        />
                      </div>
                      <div>
                        <h3 className="font-bold">{bot.name}</h3>
                        <p className="text-sm text-gray-500">
                          Created {bot.createdAt}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
                      <span className="text-sm font-medium">
                        {bot.stats?.customerSatisfaction ?? 0}%
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {bot.description ?? "No description available."}
                  </p>
                  <div className="grid grid-cols-2 gap-2 mb-4">
                    <div className="bg-gray-50 p-2 rounded">
                      <p className="text-xs text-gray-500">Conversations</p>
                      <p className="font-medium">
                        {bot.stats?.conversations?.toLocaleString() ?? 0}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-2 rounded">
                      <p className="text-xs text-gray-500">Leads</p>
                      <p className="font-medium">
                        {bot.stats?.leadGeneration?.toLocaleString() ?? 0}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-2 rounded">
                      <p className="text-xs text-gray-500">Conversion</p>
                      <p className="font-medium">
                        {bot.stats?.conversionRate ?? 0}%
                      </p>
                    </div>
                    <div className="bg-gray-50 p-2 rounded">
                      <p className="text-xs text-gray-500">Response Time</p>
                      <p className="font-medium">
                        {bot.stats?.avgResponseTime ?? "N/A"}
                      </p>
                    </div>
                  </div>
                  <Button asChild variant="outline" className="w-full">
                    <Link href={`/bots/${bot.id}`}>
                      Manage Bot <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="col-span-3 text-center py-12 bg-gray-50 rounded-lg">
              <p className="text-gray-500 mb-4">You haven't created any bots yet.</p>
              <Button asChild>
                <Link href="/create-bot">Create Your First Bot</Link>
              </Button>
            </div>
          )}
          {/* Create New Bot Card */}
          {bots.length > 0 && (
            <Card className="border-dashed border-2 border-gray-300 bg-gray-50 hover:bg-gray-100 transition-colors">
              <CardContent className="p-6 flex flex-col items-center justify-center h-full text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-3">
                  <Link href="/create-bot">
                    <Plus className="h-6 w-6 text-purple-600" />
                  </Link>
                </div>
                <h3 className="font-medium mb-2">Create New Bot</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Build a custom AI chatbot for your specific needs
                </p>
                <Button asChild variant="outline">
                  <Link href="/create-bot">Get Started</Link>
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      )}
      
    </ContentLayout>
  );
}