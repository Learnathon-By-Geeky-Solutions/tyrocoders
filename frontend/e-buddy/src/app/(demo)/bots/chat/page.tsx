'use client'

import dynamic from "next/dynamic";
import Link from "next/link";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

// Dynamically import Chat to disable SSR since it uses browser-specific APIs (e.g. WebSocket)
const Chat = dynamic(() => import("@/components/Chat").then((mod) => mod.Chat), { ssr: false });

export default function BotChatPage() {
  return (
    <ContentLayout title="Bots Chat">
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
              <Link href="/bots">Bots</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Chat</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Insert the Chat component */}
      <Chat />

      {/* Optionally, add other content below
      <PlaceholderContent /> */}
    </ContentLayout>
  );
}
