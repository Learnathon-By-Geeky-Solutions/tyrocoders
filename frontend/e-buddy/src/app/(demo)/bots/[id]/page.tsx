import { dummyBots } from '@/data/botData';
import dynamic from 'next/dynamic';
import { Suspense } from 'react';

// Dynamically import the client component without SSR
const BotDetailPageClient = dynamic(() => import('./BotDetailPageClient'));

interface ParamsProps {
  params: {
    id: string;
  };
}

export default async function BotDetailPage(props: ParamsProps) {
  // Await the dynamic parameters before accessing them
  const params = await Promise.resolve(props.params); // Ensure params are resolved
  const { id } = params;

  // Find the fallback bot data
  const fallbackBot = dummyBots.find((bot) => bot.id.toString() === id);

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <BotDetailPageClient id={id} fallbackBot={fallbackBot} />
    </Suspense>
  );
}
