import { ChatInput } from "@/components/custom/chatinput";
import { PreviewMessage, ThinkingMessage } from "@/components/custom/message";
import { useScrollToBottom } from "@/components/custom/use-scroll-to-bottom";
import { useState, useRef, useEffect } from "react";
import { message } from "@/components/interfaces/interfaces";
import { Overview } from "@/components/custom/overview";
import { Header } from "@/components/custom/header";
import { v4 as uuidv4 } from "uuid";

// Define interfaces that match the exact structure from the prompt
export interface Product {
  row_index: number;
  url: string;
  name: string;
  price: string;
  image: string;
  description_summary?: string;
  key_features?: string[];
  ratings?: string;
  availability?: string;
  processor?: string;
  material?: string;
  size_options?: string[];
  [key: string]: any; // For other comparison attributes
}

export interface ProductQueryResponse {
  response: string;
  display_type: "text" | "product_card" | "product_grid" | "comparison_table";
  follow_up_question?: string;
  products?: Product[];
}

export interface NonProductQueryResponse {
  response: string;
  display_type: "text";
  follow_up_question?: string;
  conversation_type: "casual" | "support" | "irrelevant";
}

// Union type for all response formats
export type ChatbotResponse = ProductQueryResponse | NonProductQueryResponse;

function isProductResponse(
  response: ChatbotResponse
): response is ProductQueryResponse {
  return (
    response.display_type === "product_card" ||
    response.display_type === "product_grid" ||
    response.display_type === "comparison_table"
  );
}

const socket = new WebSocket("ws://localhost:8090"); // Change to your websocket endpoint

export function Chat() {
  const [messagesContainerRef, messagesEndRef] =
    useScrollToBottom<HTMLDivElement>();
  const [messages, setMessages] = useState<message[]>([]);
  const [question, setQuestion] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [socketConnected, setSocketConnected] = useState<boolean>(false);
  const [debugMessages, setDebugMessages] = useState<string[]>([]);

  const messageHandlerRef = useRef<((event: MessageEvent) => void) | null>(
    null
  );

  // Debug logger function
  const logDebug = (msg: string) => {
    console.log(msg);
    setDebugMessages((prev) => [
      ...prev,
      `${new Date().toLocaleTimeString()}: ${msg}`,
    ]);
  };

  // Handle socket connection events
  useEffect(() => {
    const handleOpen = () => {
      logDebug("WebSocket connection established");
      setSocketConnected(true);
    };

    const handleClose = () => {
      logDebug("WebSocket connection closed");
      setSocketConnected(false);
    };

    const handleError = (error: Event) => {
      logDebug(`WebSocket error: ${error.type}`);
      setSocketConnected(false);
    };

    socket.addEventListener("open", handleOpen);
    socket.addEventListener("close", handleClose);
    socket.addEventListener("error", handleError);

    return () => {
      socket.removeEventListener("open", handleOpen);
      socket.removeEventListener("close", handleClose);
      socket.removeEventListener("error", handleError);
    };
  }, []);

  const cleanupMessageHandler = () => {
    if (messageHandlerRef.current && socket) {
      socket.removeEventListener("message", messageHandlerRef.current);
      messageHandlerRef.current = null;
    }
  };

  async function handleSubmit(text?: string) {
    if (!socket || socket.readyState !== WebSocket.OPEN || isLoading) return;

    const messageText = text || question;
    if (!messageText.trim()) return;

    setIsLoading(true);
    cleanupMessageHandler();

    const traceId = uuidv4();
    setMessages((prev) => [
      ...prev,
      { content: messageText, role: "user", id: traceId },
    ]);

    const messageData = {
      chatbot_id: "chatbot_A", // You'd need to add UI for selecting which bot to use
      query: messageText,
    };

    logDebug(`Sending: ${JSON.stringify(messageData)}`);
    socket.send(JSON.stringify(messageData));
    setQuestion("");

    try {
      const messageHandler = (event: MessageEvent) => {
        setIsLoading(false);
        logDebug(
          `Received raw data: ${event.data.slice(0, 200)}${
            event.data.length > 200 ? "..." : ""
          }`
        );

        try {
          // Try to parse as JSON first
          let responseData: ChatbotResponse;

          if (typeof event.data === "string") {
            responseData = JSON.parse(event.data);
          } else {
            responseData = event.data;
          }

          logDebug(
            `Parsed data: ${JSON.stringify(responseData).slice(0, 200)}...`
          );

          // Ensure we have at least these base properties
          if (
            !("response" in responseData) ||
            !("display_type" in responseData)
          ) {
            throw new Error("Invalid response format: missing required fields");
          }

          const newAssistantMessage = {
            content: responseData.response,
            role: "assistant",
            id: traceId,
            display_type: responseData.display_type,
            follow_up_question: responseData.follow_up_question,
            products: isProductResponse(responseData)
              ? responseData.products
              : undefined,
            conversation_type: (responseData as NonProductQueryResponse)
              .conversation_type,
          };

          setMessages((prev) => [...prev, newAssistantMessage]);
        } catch (error) {
          logDebug(`Failed to parse JSON: ${error}`);

          let displayText;
          if (typeof event.data === "string") {
            displayText = event.data;
          } else if (event.data instanceof Blob) {
            const reader = new FileReader();
            reader.onload = function () {
              const text = reader.result as string;
              setMessages((prev) => [
                ...prev,
                {
                  content: text || "Could not read response data",
                  role: "assistant",
                  id: traceId,
                  display_type: "text",
                },
              ]);
            };
            reader.readAsText(event.data);
            displayText = "Loading blob data...";
          } else {
            displayText = "Received non-text response: " + typeof event.data;
          }

          setMessages((prev) => [
            ...prev,
            {
              content: displayText,
              role: "assistant",
              id: traceId,
              display_type: "text",
            },
          ]);
        }

        cleanupMessageHandler();
      };

      messageHandlerRef.current = messageHandler;
      socket.addEventListener("message", messageHandler);
    } catch (error) {
      console.error("WebSocket error:", error);
      setIsLoading(false);
      logDebug(`Error handling message: ${error}`);

      setMessages((prev) => [
        ...prev,
        {
          content: "Error communicating with the server. Please try again.",
          role: "assistant",
          id: traceId,
          display_type: "text",
        },
      ]);
    }
  }

  return (
    <div className="flex flex-col min-w-0 h-dvh bg-gradient-to-br from-gray-100 to-gray-200">
      <Header />
      <div
        className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4 px-4"
        ref={messagesContainerRef}
      >
        {messages.length === 0 && <Overview />}

        {messages.map((msg, index) => (
          <ChatMessage
            key={msg.id || index}
            message={msg}
            onFollowUpClick={handleSubmit}
          />
        ))}

        {debugMessages.length > 0 && (
          <div className="px-4 md:px-6 max-w-3xl mx-auto w-full mt-4 border-t pt-4">
            <details className="cursor-pointer">
              <summary className="text-sm text-gray-600">
                Debug Logs ({debugMessages.length})
              </summary>
              <pre className="mt-2 p-2 bg-gray-100 rounded-md text-xs overflow-x-auto max-h-64">
                {debugMessages.map((msg: string, idx: number) => (
                  <div key={idx}>{msg}</div>
                ))}
              </pre>
            </details>
          </div>
        )}

        {isLoading && <ThinkingMessage />}
        <div
          ref={messagesEndRef}
          className="shrink-0 min-w-[24px] min-h-[24px]"
        />
      </div>
      <div className="flex mx-auto px-4 bg-white pb-4 md:pb-6 gap-2 w-full md:max-w-3xl shadow-inner">
        <ChatInput
          question={question}
          setQuestion={setQuestion}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}

// Enhanced message component that handles both standard messages and special display types
function ChatMessage({
  message,
  onFollowUpClick,
}: {
  message: message & Partial<ChatbotResponse>;
  onFollowUpClick: (text: string) => void;
}) {
  if (message.role === "user") {
    return <PreviewMessage message={message} />;
  }

  switch (message.display_type) {
    case "product_card":
      return (
        <ProductCardDisplay
          message={message}
          onFollowUpClick={onFollowUpClick}
        />
      );
    case "product_grid":
      return (
        <ProductGridDisplay
          message={message}
          onFollowUpClick={onFollowUpClick}
        />
      );
    case "comparison_table":
      return (
        <ComparisonTableDisplay
          message={message}
          onFollowUpClick={onFollowUpClick}
        />
      );
    case "text":
    default:
      return (
        <TextMessageDisplay
          message={message}
          onFollowUpClick={onFollowUpClick}
        />
      );
  }
}

// Component for simple text responses
function TextMessageDisplay({
  message,
  onFollowUpClick,
}: {
  message: any;
  onFollowUpClick: (text: string) => void;
}) {
  return (
    <div className="flex flex-col px-4 md:px-6 max-w-3xl mx-auto w-full">
      <div className="flex items-start gap-4 md:gap-6">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border bg-blue-500 text-white shadow-md">
          {/* Custom avatar icon */}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 256 256"
            fill="currentColor"
            className="h-5 w-5"
          >
            <path d="M230.92 212c-15.23-26.33-38.7-45.21-66.09-54.16a72 72 0 1 0-73.66 0c-27.39 8.94-50.86 27.82-66.09 54.16a8 8 0 1 0 13.85 8c18.84-32.56 52.14-52 89.07-52s70.23 19.44 89.07 52a8 8 0 1 0 13.85-8ZM72 96a56 56 0 1 1 56 56 56.06 56.06 0 0 1-56-56Z"></path>
          </svg>
        </div>
        <div className="flex flex-col flex-1 gap-4">
          <div className="prose dark:prose-dark">
            <p>{message.content}</p>
          </div>
          {message.follow_up_question && (
            <button
              onClick={() => onFollowUpClick(message.follow_up_question!)}
              className="self-start rounded-md bg-blue-100 px-4 py-2 text-sm text-blue-600 hover:bg-blue-200 transition-colors"
            >
              {message.follow_up_question}
            </button>
          )}
          {message.conversation_type && (
            <span className="inline-flex items-center rounded-full bg-gray-200 px-2 py-1 text-xs text-gray-700">
              {message.conversation_type}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

// Component for single product card display
function ProductCardDisplay({
  message,
  onFollowUpClick,
}: {
  message: any & { products?: Product[] };
  onFollowUpClick: (text: string) => void;
}) {
  const products: Product[] = message.products || [];
  if (products.length === 0) {
    return (
      <TextMessageDisplay message={message} onFollowUpClick={onFollowUpClick} />
    );
  }
  const product: Product = products[0];

  return (
    <div className="flex flex-col px-4 md:px-6 max-w-3xl mx-auto w-full">
      <div className="flex items-start gap-4 md:gap-6">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border bg-green-500 text-white shadow-md">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 256 256"
            fill="currentColor"
            className="h-5 w-5"
          >
            <path d="M230.92 212c-15.23-26.33-38.7-45.21-66.09-54.16a72 72 0 1 0-73.66 0c-27.39 8.94-50.86 27.82-66.09 54.16a8 8 0 1 0 13.85 8c18.84-32.56 52.14-52 89.07-52s70.23 19.44 89.07 52a8 8 0 1 0 13.85-8ZM72 96a56 56 0 1 1 56 56 56.06 56.06 0 0 1-56-56Z"></path>
          </svg>
        </div>
        <div className="flex flex-col flex-1 gap-4">
          <div className="prose dark:prose-dark">
            <p>{message.content}</p>
          </div>
          <div className="mt-4 border rounded-lg shadow-lg overflow-hidden">
            <div className="w-full h-64 bg-gray-100 flex items-center justify-center">
              <img
                src={product.image || "/api/placeholder/400/320"}
                alt={product.name}
                className="w-full h-full object-cover transition-all duration-300 hover:scale-105"
              />
            </div>
            <div className="p-4">
              <h3 className="font-bold text-xl mb-1">{product.name}</h3>
              <p className="text-lg font-semibold text-green-600 mb-2">
                {product.price}
              </p>
              {product.description_summary && (
                <p className="text-gray-700 mb-3">
                  {product.description_summary}
                </p>
              )}
              {product.key_features && product.key_features.length > 0 && (
                <div className="mt-2">
                  <h4 className="text-sm font-medium mb-1">Key Features:</h4>
                  <ul className="list-disc pl-5 text-sm text-gray-600">
                    {product.key_features.map(
                      (feature: string, index: number) => (
                        <li key={index}>{feature}</li>
                      )
                    )}
                  </ul>
                </div>
              )}
              {product.availability && (
                <p className="mt-2 text-sm text-gray-600">
                  <strong>Availability:</strong> {product.availability}
                </p>
              )}
              <a
                href={product.url}
                className="mt-4 inline-block rounded-md bg-green-500 px-4 py-2 text-sm text-white shadow hover:bg-green-600 transition-colors"
              >
                View Product
              </a>
            </div>
          </div>
          {message.follow_up_question && (
            <button
              onClick={() => onFollowUpClick(message.follow_up_question!)}
              className="self-start mt-4 rounded-md bg-green-50 px-4 py-2 text-sm text-green-600 hover:bg-green-100 transition-colors"
            >
              {message.follow_up_question}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// Component for multiple product grid display
function ProductGridDisplay({
  message,
  onFollowUpClick,
}: {
  message: any & { products?: Product[] };
  onFollowUpClick: (text: string) => void;
}) {
  const products: Product[] = message.products || [];
  if (products.length === 0) {
    return (
      <TextMessageDisplay message={message} onFollowUpClick={onFollowUpClick} />
    );
  }
  return (
    <div className="flex flex-col px-4 md:px-6 max-w-3xl mx-auto w-full">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {products.map((product: Product, index: number) => (
          <div
            key={index}
            className="border rounded-lg overflow-hidden shadow-md transition-transform duration-300 hover:-translate-y-1"
          >
            <div className="w-full h-48 bg-gray-100 flex items-center justify-center overflow-hidden">
              <img
                src={product.image || "/api/placeholder/400/320"}
                alt={product.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="p-3">
              <h3 className="font-bold text-sm mb-1 truncate">
                {product.name}
              </h3>
              <p className="text-sm font-semibold text-green-600">
                {product.price}
              </p>
              <a
                href={product.url}
                className="mt-2 inline-block rounded-md bg-green-500 px-3 py-1 text-xs text-white shadow hover:bg-green-600 transition-colors"
              >
                View Details
              </a>
            </div>
          </div>
        ))}
      </div>
      {message.follow_up_question && (
        <button
          onClick={() => onFollowUpClick(message.follow_up_question!)}
          className="self-start mt-4 rounded-md bg-green-50 px-4 py-2 text-sm text-green-600 hover:bg-green-100 transition-colors"
        >
          {message.follow_up_question}
        </button>
      )}
    </div>
  );
}

// Component for product comparison table
function ComparisonTableDisplay({
  message,
  onFollowUpClick,
}: {
  message: any & { products?: Product[] };
  onFollowUpClick: (text: string) => void;
}) {
  const products: Product[] = message.products || [];
  if (products.length < 2) {
    return (
      <TextMessageDisplay message={message} onFollowUpClick={onFollowUpClick} />
    );
  }

  // Get comparison properties excluding standard ones
  const standardProps = [
    "row_index",
    "url",
    "name",
    "price",
    "image",
    "description_summary",
  ];
  const allProps = new Set<string>();
  products.forEach((product: Product) => {
    Object.keys(product).forEach((key: string) => {
      if (!standardProps.includes(key)) {
        allProps.add(key);
      }
    });
  });
  const comparisonProps = Array.from(allProps);

  return (
    <div className="flex flex-col px-4 md:px-6 max-w-3xl mx-auto w-full">
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse border">
          <thead>
            <tr className="bg-gray-200">
              <th className="border p-2 text-left">Features</th>
              {products.map((product: Product, index: number) => (
                <th key={index} className="border p-2 text-left">
                  {product.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="border p-2 font-medium">Image</td>
              {products.map((product: Product, index: number) => (
                <td key={index} className="border p-2">
                  <div className="h-16 w-16 bg-gray-100 flex items-center justify-center overflow-hidden">
                    <img
                      src={product.image || "/api/placeholder/64/64"}
                      alt={product.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                </td>
              ))}
            </tr>
            <tr>
              <td className="border p-2 font-medium">Price</td>
              {products.map((product: Product, index: number) => (
                <td key={index} className="border p-2 font-bold text-green-600">
                  {product.price}
                </td>
              ))}
            </tr>
            {comparisonProps.map((prop: string) => (
              <tr key={prop}>
                <td className="border p-2 font-medium">
                  {prop.charAt(0).toUpperCase() +
                    prop.slice(1).replace(/_/g, " ")}
                </td>
                {products.map((product: Product, index: number) => (
                  <td key={index} className="border p-2">
                    {Array.isArray(product[prop])
                      ? product[prop].join(", ")
                      : product[prop] !== undefined
                      ? String(product[prop])
                      : "—"}
                  </td>
                ))}
              </tr>
            ))}
            <tr>
              <td className="border p-2"></td>
              {products.map((product: Product, index: number) => (
                <td key={index} className="border p-2">
                  <a
                    href={product.url}
                    className="inline-block rounded-md bg-green-500 px-3 py-1 text-xs font-medium text-white shadow hover:bg-green-600 transition-colors"
                  >
                    View Details
                  </a>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
      {message.follow_up_question && (
        <button
          onClick={() => onFollowUpClick(message.follow_up_question!)}
          className="self-start mt-4 rounded-md bg-green-50 px-4 py-2 text-sm text-green-600 hover:bg-green-100 transition-colors"
        >
          {message.follow_up_question}
        </button>
      )}
    </div>
  );
}
