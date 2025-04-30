"use client";

import React, { useState } from "react";
import { Code } from "lucide-react";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github.css"; // ensure this CSS is included globally

interface ChatEmbedGeneratorProps {
  chatbotId: string;
}

const ChatEmbedGenerator: React.FC<ChatEmbedGeneratorProps> = ({
  chatbotId,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  // Base URLs for your script and API endpoints
  const scriptUrl =
    process.env.NEXT_PUBLIC_FRONTEND_URL || "http://localhost:3000";
  const backendEndpoint =
    process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  // This is the code that will be embedded on client websites
  const embedCode = `<!-- Chat Widget Embed Code -->
<div id=\"chat-widget-root\"></div>
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

  // Wrap in markdown code fence so ReactMarkdown can highlight
  const markdownCode = `\`\`\`js
${embedCode}
\`\`\``;

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(embedCode);
      // Optionally, you can set local state to indicate 'copied' for UI feedback
    } catch (err) {
      console.error("Failed to copy embed code:", err);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <button
          className="p-2 rounded hover:bg-gray-100 transition"
          title="Embed Widget"
          onClick={(e) => {
            e.stopPropagation();
            setIsOpen(true);
          }}
        >
          <Code className="h-5 w-5 text-gray-600 hover:text-indigo-600" />
        </button>
      </DialogTrigger>

      <DialogContent className="w-[80vw] max-w-xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Embed Chat Widget</DialogTitle>
          <DialogDescription>
            Insert the following JavaScript snippet into your HTML’s{" "}
            <code>&lt;head&gt;</code> section to activate the chat widget on
            your site.
          </DialogDescription>
        </DialogHeader>

        <div className="mt-4 flex-1 overflow-auto prose max-w-full">
          <ReactMarkdown
            children={markdownCode}
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeSanitize, rehypeHighlight]}
          />
        </div>

        <DialogFooter className="pt-4 flex justify-end space-x-2">
          <Button onClick={copyToClipboard}>Copy Code</Button>
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ChatEmbedGenerator;
