import { dummyBots } from '@/data/botData';
import dynamic from 'next/dynamic';
import { Suspense } from 'react';

// Dynamically import the client component without SSR
const BotDetailPageClient = dynamic(() => import('./BotDetailPageClient'), {
  loading: () => <div>Loading bot details...</div>
});

interface ParamsProps {
  params: {
    id: string;
  };
}

export default async function BotDetailPage(props: Readonly<ParamsProps>) {
  const params = await Promise.resolve(props.params);
  const { id } = params;

  // Find the fallback bot data
  const fallbackBot = dummyBots.find((bot) => bot.id.toString() === id);
  
  return (
    <Suspense fallback={<div>Loading bot details...</div>}>
      <BotDetailPageClient id={id} fallbackBot={fallbackBot} />
    </Suspense>
  );
}