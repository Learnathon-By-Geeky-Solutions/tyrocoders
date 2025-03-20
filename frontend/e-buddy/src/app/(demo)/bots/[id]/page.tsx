'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { ContentLayout } from '@/components/admin-panel/content-layout';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { UserCircle } from 'lucide-react';

const dummyBots = [
  {
    id: 1,
    name: 'ChatBot Alpha',
    model: 'GPT-3',
    createdAt: '2023-01-01',
    description:
      'ChatBot Alpha is powered by GPT-3 and excels in general conversation. It can be used for customer interactions, support, and more.',
  },
  {
    id: 2,
    name: 'SupportBot Beta',
    model: 'BERT',
    createdAt: '2023-02-15',
    description:
      'SupportBot Beta leverages the BERT model to provide top-notch customer support and quick answers to user queries.',
  },
  {
    id: 3,
    name: 'SalesBot Gamma',
    model: 'GPT-4',
    createdAt: '2023-03-20',
    description:
      'SalesBot Gamma utilizes GPT-4 to boost your sales efforts with intelligent conversation flows and persuasive dialogue.',
  },
];

export default function BotDetailPage() {
  const params = useParams();
  const { id } = params;

  const bot = dummyBots.find((bot) => bot.id.toString() === id);

  if (!bot) {
    return (
      <ContentLayout title="Bot Details">
        <p>Bot not found.</p>
      </ContentLayout>
    );
  }

  return (
    <ContentLayout title={bot.name}>
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
              <Link href="/bots/my-bots">My Bots</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>{bot.name}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      <div className="mt-6">
        <Card className="shadow-lg border border-gray-200 rounded-lg overflow-hidden">
          <CardHeader className="relative">
            {/* Hero image from an online source */}
            <Image 
              src="https://source.unsplash.com/800x300/?technology,bot" 
              alt={`${bot.name} Hero`} 
              width={800} 
              height={300} 
              className="object-cover w-full h-48" 
            />
            {/* Icon overlay */}
            <div className="absolute top-4 left-4 bg-white rounded-full p-2 shadow-md">
              <UserCircle className="w-10 h-10 text-blue-600" />
            </div>
          </CardHeader>
          <CardContent className="p-6 bg-white">
            <h1 className="text-3xl font-bold text-gray-800">{bot.name}</h1>
            <p className="mt-2 text-gray-600">
              <span className="font-semibold">Model:</span> {bot.model}
            </p>
            <p className="mt-2 text-gray-600">
              <span className="font-semibold">Created At:</span> {bot.createdAt}
            </p>
            <p className="mt-4 text-gray-800">{bot.description}</p>
            {/* Additional Links for Bot Information */}
            <div className="mt-6 space-y-2">
              <Link
                href={`/bots/${bot.id}/conversation`}
                className="block text-blue-600 hover:underline"
              >
                View Conversation History
              </Link>
              <Link
                href={`/bots/${bot.id}/queries`}
                className="block text-blue-600 hover:underline"
              >
                View Queries
              </Link>
              <Link
                href={`/bots/${bot.id}/model`}
                className="block text-blue-600 hover:underline"
              >
                View Model Details
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </ContentLayout>
  );
}
