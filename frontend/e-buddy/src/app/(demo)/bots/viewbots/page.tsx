"use client";

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
import { ArrowRight, MessageSquare, Star, Plus } from "lucide-react";
import { dummyBots } from "@/data/botData"; // external data

export default function MyBotsPage() {
  const router = useRouter();

  const handleRowClick = (id: number) => {
    router.push(`/bots/${id}`);
  };

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
      <h2 className="text-xl font-bold mb-4">Your Chatbots</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {dummyBots.map((bot) => (
          <Card key={bot.id} className="overflow-hidden hover:shadow-lg transition-shadow">
            <div
              className="h-3"
              style={{
                backgroundColor: bot.customization?.primaryColor || "#000"
              }}
            />
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center"
                    style={{
                      backgroundColor:
                        (bot.customization?.primaryColor || "#000") + "20"
                    }}
                  >
                    <MessageSquare
                      className="h-5 w-5"
                      style={{ color: bot.customization?.primaryColor || "#000" }}
                    />
                  </div>
                  <div>
                    <h3 className="font-bold">{bot.name}</h3>
                    <p className="text-sm text-gray-500">Created {bot.createdAt}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
                  <span className="text-sm font-medium">
                    {bot.stats?.customerSatisfaction || 0}%
                  </span>
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                {bot.description || "No description available."}
              </p>

              <div className="grid grid-cols-2 gap-2 mb-4">
                <div className="bg-gray-50 p-2 rounded">
                  <p className="text-xs text-gray-500">Conversations</p>
                  <p className="font-medium">
                    {bot.stats?.conversations?.toLocaleString() || 0}
                  </p>
                </div>
                <div className="bg-gray-50 p-2 rounded">
                  <p className="text-xs text-gray-500">Leads</p>
                  <p className="font-medium">
                    {bot.stats?.leadGeneration?.toLocaleString() || 0}
                  </p>
                </div>
                <div className="bg-gray-50 p-2 rounded">
                  <p className="text-xs text-gray-500">Conversion</p>
                  <p className="font-medium">
                    {bot.stats?.conversionRate || 0}%
                  </p>
                </div>
                <div className="bg-gray-50 p-2 rounded">
                  <p className="text-xs text-gray-500">Response Time</p>
                  <p className="font-medium">
                    {bot.stats?.avgResponseTime || "N/A"}
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
        ))}

        {/* Create New Bot Card */}
        <Card className="border-dashed border-2 border-gray-300 bg-gray-50 hover:bg-gray-100 transition-colors">
          <CardContent className="p-6 flex flex-col items-center justify-center h-full text-center">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-3">
              <Link href={`/bots/setup`}>
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
      </div>
    </ContentLayout>
  );
}
