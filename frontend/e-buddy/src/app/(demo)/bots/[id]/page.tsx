// This is a server component – do NOT include "use client" here
import BotDetailPageClient from './BotDetailPageClient';
import { dummyBots } from '@/data/botData';

interface ParamsProps {
  params: {
    id: string;
  };
}

// Export generateStaticParams to satisfy the "output: export" configuration.
export async function generateStaticParams() {
  return dummyBots.map((bot) => ({ id: bot.id.toString() }));
}

// The main page is a server component that finds the correct bot and passes it to the client component.
export default  function BotDetailPage({ params }: ParamsProps) {
  const bot =  dummyBots.find((bot) => bot.id.toString() === params.id);

  if (!bot) {
    return <p>Bot not found.</p>;
  }

  return <BotDetailPageClient bot={bot} />;
}
