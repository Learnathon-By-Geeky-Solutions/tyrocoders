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
} from "lucide-react";
import { botAPI } from "@/services/api";
import { Bot } from "@/data/botData";

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
          createdAt: api.created_at?.split("T")[0] || "—",
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

  const handleSort = (key: "name" | "createdAt") => {
    setSortConfig((current) => {
      if (current?.key === key) {
        return { key, direction: current.direction === "asc" ? "desc" : "asc" };
      }
      return { key, direction: "asc" };
    });
  };

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
          <Link href="/create-bot">
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
        <div className="overflow-hidden bg-white shadow-md rounded-lg">
          {/* Header */}
          <div className="hidden sm:grid grid-cols-12 gap-4 p-4 bg-gray-100 text-gray-600 font-medium border-b">
            <div
              className="col-span-4 flex items-center cursor-pointer"
              onClick={() => handleSort("name")}
            >
              <span>Name</span>
              <span className="ml-2">
                {!sortConfig || sortConfig.key !== "name" ? (
                  <ChevronsUpDown className="h-4 w-4 text-gray-500" />
                ) : sortConfig.direction === "asc" ? (
                  <ChevronUp className="h-4 w-4 text-gray-500" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-gray-500" />
                )}
              </span>
            </div>
            <div className="col-span-3">Model</div>
            <div
              className="col-span-2 flex items-center cursor-pointer"
              onClick={() => handleSort("createdAt")}
            >
              <span>Created</span>
              <span className="ml-2">
                {!sortConfig || sortConfig.key !== "createdAt" ? (
                  <ChevronsUpDown className="h-4 w-4 text-gray-500" />
                ) : sortConfig.direction === "asc" ? (
                  <ChevronUp className="h-4 w-4 text-gray-500" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-gray-500" />
                )}
              </span>
            </div>
            <div className="col-span-3 text-right">Actions</div>
          </div>

          {/* Rows */}
          {sortedBots.length ? (
            sortedBots.map((bot) => (
              <div
                key={bot.id}
                className="grid grid-cols-1 sm:grid-cols-12 gap-4 items-center p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                onClick={() => router.push(`/bots/${bot.id}`)}
              >
                <div className="col-span-1 sm:col-span-4 flex items-center space-x-3">
                  <div className="p-2 bg-indigo-100 rounded">
                    <MessageSquare className="h-5 w-5 text-indigo-500" />
                  </div>
                  <span className="font-semibold text-gray-800">
                    {bot.name}
                  </span>
                </div>
                <div className="col-span-1 sm:col-span-3 text-gray-700">
                  {bot.model}
                </div>
                <div className="col-span-1 sm:col-span-2 text-gray-500">
                  {bot.createdAt}
                </div>
                <div className="col-span-1 sm:col-span-3 flex justify-end space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/bots/${bot.id}`);
                    }}
                    title="Embed Widget"
                    className="p-2 rounded hover:bg-gray-100"
                  >
                    <Code className="h-5 w-5 text-gray-600 hover:text-indigo-600" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/bots/${bot.id}/edit`);
                    }}
                    title="Edit Bot"
                    className="p-2 rounded hover:bg-gray-100"
                  >
                    <Edit2 className="h-5 w-5 text-gray-600 hover:text-indigo-600" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation(); /* TODO: delete handler */
                    }}
                    title="Delete Bot"
                    className="p-2 rounded hover:bg-red-100"
                  >
                    <Trash2 className="h-5 w-5 text-gray-600 hover:text-red-600" />
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="p-6 text-center text-gray-500">
              You haven’t created any bots yet.
            </div>
          )}
        </div>
      )}
    </ContentLayout>
  );
}
