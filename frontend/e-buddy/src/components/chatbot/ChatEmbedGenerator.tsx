import React, { useState } from 'react';

const ChatEmbedGenerator: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
//   data-user-id="67fa4ef32db2ee2e5e3abb2f"
//         data-chatbot-id="6803ce5b4c0a170434b221fc"
// /api/v1/chatbot-embed/chatbot-conversation/read/{conversation_id}
// /api/v1/chatbot-embed/chatbot-conversation/start/{chatbot_id}
  const scriptUrl = 'http://localhost:3000/chat-widget.js';
  const backendEndpoint = 'http://127.0.0.1:8000/api/v1/chatbot-embed/chatbot-conversation/start/6803ce5b4c0a170434b221fc';
  const loaderUrl = 'http://localhost:3000/chat-widget-loader.js';

  // This is the code that will be embedded on client websites
  const embedCode = `<!-- Chat Widget Embed Code -->
<div id="chat-widget-root"></div>
<script>
  (function() {
    var script = document.createElement('script');
    script.src = "${loaderUrl.replace('WIDGET_URL_PLACEHOLDER', scriptUrl).replace('API_ENDPOINT_PLACEHOLDER', backendEndpoint)}";
    script.async = true;
    document.head.appendChild(script);
  })();
</script>`;

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center p-2 bg-blue-600 hover:bg-blue-700 text-white rounded"
      >
        Get Embed Code
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-lg w-96 p-6">
            <h2 className="text-xl font-semibold mb-4">Embed Code</h2>
            <textarea
              readOnly
              className="w-full h-40 p-2 border border-gray-300 rounded mb-4 font-mono text-sm"
              value={embedCode}
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => navigator.clipboard.writeText(embedCode)}
                className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded"
              >
                Copy
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