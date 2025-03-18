"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Bot, FileText, FileStack, HelpCircle, ArrowUpRight } from "lucide-react";

type StatCardProps = {
  icon: React.ElementType;
  title: string;
  count: number;
  link: string;
};

const StatCard = ({ icon: Icon, title, count, link }: StatCardProps) => (
  <Link href={link} className="group">
    <Card className="flex items-center p-4 gap-4 border border-gray-200 bg-white rounded-lg shadow-sm hover:shadow-xl transition transform hover:scale-105">
      <Icon className="w-10 h-10 text-blue-500 group-hover:text-blue-700" />
      <div>
        <CardTitle className="text-xl font-bold text-gray-800">{title}</CardTitle>
        <p className="text-3xl font-extrabold text-black">{count}</p>
      </div>
    </Card>
  </Link>
);

type InfoCardProps = {
  title: string;
  description: string;
  link: string;
};

const InfoCard = ({ title, description, link }: InfoCardProps) => (
  <Card className="p-6 border border-gray-200 bg-white rounded-lg shadow-sm hover:shadow-xl transition transform hover:scale-105">
    <CardHeader>
      <CardTitle className="text-2xl font-bold text-gray-800">{title}</CardTitle>
    </CardHeader>
    <CardContent className="flex justify-between items-center mt-4">
      <p className="text-gray-600 text-base">{description}</p>
      <Link href={link} className="text-blue-500 flex items-center gap-1 hover:text-blue-700">
        <ArrowUpRight className="w-5 h-5" />
      </Link>
    </CardContent>
  </Card>
);

export function DashboardCards() {
  return (
    <div className="grid gap-6">
      {/* First Row */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard icon={Bot} title="Bots" count={12} link="/bots" />
        <StatCard icon={FileStack} title="Sources" count={34} link="/sources" />
        <StatCard icon={FileText} title="Pages" count={56} link="/pages" />
        <StatCard icon={HelpCircle} title="Questions" count={78} link="/questions" />
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-2 gap-6">
        <InfoCard title="View Bots" description="Manage and monitor your bots" link="/bots/view" />
        <InfoCard title="Train Bots" description="Train your AI bots for better performance" link="/bots/train" />
      </div>

      {/* Third Row */}
      <div className="grid grid-cols-2 gap-6">
        <InfoCard title="Plan & Billing" description="Manage your subscription and billing" link="/billing" />
        <InfoCard title="Teams & Collaboration" description="Invite and manage team members" link="/teams" />
      </div>
    </div>
  );
}
