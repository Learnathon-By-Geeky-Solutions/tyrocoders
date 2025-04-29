import React, { useState } from 'react';
import { Code } from 'lucide-react'; // Assuming you're using lucide-react

interface ChatEmbedGeneratorProps {
  chatbotId: string;
}

const ChatEmbedGenerator: React.FC<ChatEmbedGeneratorProps> = ({ chatbotId }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  // Base URLs for your script and API endpoints
  const scriptUrl = process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000';
  const backendEndpoint = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
  
  // This is the code that will be embedded on client websites
  const embedCode = `<!-- Chat Widget Embed Code -->
<div id="chat-widget-root"></div>
<script>
  (function() {
    var script = document.createElement('script');
    script.src = "${scriptUrl}/chat-widget-loader.js";
    script.async = true;
    script.setAttribute('data-chatbot-id', "${chatbotId}");
    script.setAttribute('data-api-endpoint', "${backendEndpoint}/api/v1");
    document.head.appendChild(script);
  })();
</script>`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(embedCode)
      .then(() => {
        // You could add a toast notification here
        alert('Embed code copied to clipboard!');
      })
      .catch(err => {
        console.error('Failed to copy: ', err);
        alert('Failed to copy to clipboard');
      });
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="p-2 rounded hover:bg-gray-100 transition"
        title="Embed Widget"
      >
        <Code className="h-5 w-5 text-gray-600 hover:text-indigo-600" />
      </button>
      
      {isOpen && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-lg w-96 p-6">
            <h2 className="text-xl font-semibold mb-4">Embed Chat Widget</h2>
            <p className="mb-4 text-sm text-gray-600">
              Copy and paste this code into your website where you want the chat widget to appear.
            </p>
            <textarea
              readOnly
              className="w-full h-40 p-2 border border-gray-300 rounded mb-4 font-mono text-sm"
              value={embedCode}
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={copyToClipboard}
                className="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded"
              >
                Copy Code
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatEmbedGenerator;