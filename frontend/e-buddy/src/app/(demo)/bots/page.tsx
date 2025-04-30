// pages/my-bots.tsx
"use client";

import React, { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Button } from "@/components/ui/button";
import {
  Loader,
  MessageSquare,
  Code,
  Edit2,
  Trash2,
  Plus,
  ChevronsUpDown,
  ChevronUp,
  ChevronDown,
  Cpu,
  Calendar,
} from "lucide-react";
import { botAPI } from "@/services/api";
import { Bot } from "@/data/botData";
import ChatEmbedGenerator from "@/components/chatbot/ChatEmbedGenerator";

export default function MyBotsPage() {
  const router = useRouter();
  const [bots, setBots] = useState<Bot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortConfig, setSortConfig] = useState<{
    key: "name" | "createdAt";
    direction: "asc" | "desc";
  } | null>(null);

  useEffect(() => {
    async function fetchBots() {
      try {
        setLoading(true);
        const response = await botAPI.getAllBots();
        const data = response.data.data || [];
        const transformed = data.map((api: any) => ({
          id: api._id,
          name: api.name,
          model: api.ai_model_name,
          createdAt:
            api.created_at || new Date().toISOString().split("T")[0],
        }));
        setBots(transformed);
      } catch (e) {
        console.error(e);
        setError("Unable to load bots.");
      } finally {
        setLoading(false);
      }
    }
    fetchBots();
  }, []);

  const sortedBots = useMemo(() => {
    if (!sortConfig) return bots;
    return [...bots].sort((a, b) => {
      let aVal: string | Date = a[sortConfig.key];
      let bVal: string | Date = b[sortConfig.key];
      if (sortConfig.key === "createdAt") {
        aVal = new Date(a.createdAt);
        bVal = new Date(b.createdAt);
      }
      if (aVal < bVal) return sortConfig.direction === "asc" ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === "asc" ? 1 : -1;
      return 0;
    });
  }, [bots, sortConfig]);

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

      <div className="flex justify-between items-center mt-6 mb-4">
        <h2 className="text-2xl font-semibold text-gray-800"></h2>
        <Button
          asChild
          variant="outline"
          className="flex items-center text-dark hover:text-white"
        >
          <Link href="/bots/setup">
            <Plus className="h-4 w-4" /> New Bot
          </Link>
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader className="h-8 w-8 animate-spin text-indigo-500" />
        </div>
      ) : error ? (
        <div className="px-4 py-6 bg-red-50 text-red-700 rounded-lg">
          {error}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {bots.length ? (
            bots.map((bot) => (
              <div
                key={bot.id}
                className="bg-white border rounded-lg shadow transition hover:shadow-lg cursor-pointer flex flex-col justify-between p-6 border-t-8 border-accent"
                onClick={() => router.push(`/bots/${bot.id}`)}
              >
                {/* Bot Header with Accent Border */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-indigo-100 rounded-full">
                      <MessageSquare className="h-5 w-5 text-indigo-500" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-800">
                      {bot.name}
                    </h3>
                  </div>
                  <span className="text-xs font-semibold bg-green-100 text-green-700 px-2 py-1 rounded-full">
                    {"Active"}
                  </span>
                </div>

                {/* Bot Details with Colorful Icons */}
                <div className="mt-4 text-gray-600 text-sm space-y-3">
                  <div className="flex items-center space-x-2">
                    <Cpu className="h-4 w-4 text-purple-500" />
                    <span>
                      <span className="font-medium">Model:</span> {bot.model}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4 text-yellow-500" />
                    <span>
                      <span className="font-medium">Created:</span>{" "}
                      {bot.createdAt}
                    </span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="mt-6 flex justify-end space-x-3">
                  {/* <button
                    onClick={(e) => {
                      e.stopPropagation();
                      // router.push(`/bots/${bot.id}`);
                    }}
                    title="Embed Widget"
                    className="p-2 rounded hover:bg-gray-100 transition"
                  >
                    <Code className="h-5 w-5 text-gray-600 hover:text-indigo-600" />
                  </button> */}

                  <div
                    onClick={(e) => {
                      e.stopPropagation();
                      /* now do whatever ChatEmbedGenerator wants to do,
         or if it has its own click handler, let it run normally */
                    }}
                  >
                    <ChatEmbedGenerator chatbotId={bot.id.toString()} />
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/bots/${bot.id}/edit`);
                    }}
                    title="Edit Bot"
                    className="p-2 rounded hover:bg-gray-100 transition"
                  >
                    <Edit2 className="h-5 w-5 text-gray-600 hover:text-indigo-600" />
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      // TODO: implement delete handler
                    }}
                    title="Delete Bot"
                    className="p-2 rounded hover:bg-red-100 transition"
                  >
                    <Trash2 className="h-5 w-5 text-gray-600 hover:text-red-600" />
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full text-center text-gray-500 p-6">
              You haven’t created any bots yet.
            </div>
          )}
        </div>
      )}
    </ContentLayout>
  );
}
