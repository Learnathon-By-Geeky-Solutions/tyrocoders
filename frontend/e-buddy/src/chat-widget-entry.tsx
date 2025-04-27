import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ChatTrigger } from '@/components/chatbot/ChatTrigger';
import { ChatPreview } from '@/components/chatbot/ChatPreview';
import { BotCustomization } from '@/types/chatbot';

const App: React.FC = () => {
  const config = (window as any).ChatWidgetConfig as BotCustomization | undefined;
  const [open, setOpen] = useState(false);

  if (!config) {
    return <div>Loading chat widget...</div>;
  }

  return (
    <>
      <ChatTrigger customization={config} onClick={() => setOpen(true)} />
      {open && <ChatPreview customization={config} onClose={() => setOpen(false)} />}
    </>
  );
};

function mountWidget() {
  let container = document.getElementById('chat-widget-root');
  if (!container) {
    container = document.createElement('div');
    container.id = 'chat-widget-root';
    document.body.appendChild(container);
  }
  const root = createRoot(container);
  root.render(<App />);
}

if (document.readyState === 'complete' || document.readyState === 'interactive') {
  mountWidget();
} else {
  document.addEventListener('DOMContentLoaded', mountWidget);
}
