import { useState, useRef, useEffect } from "react";
import { MessageSquare, Send, X, ChevronUp, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BotCustomization, ChatMessage } from "@/types/chatbot";
import { cn } from "@/lib/utils";

interface ChatPreviewProps {
  customization: BotCustomization;
  onClose: () => void;
  chatbotId?: string;
}

// Define product data structure
interface ProductData {
  id: string;
  name: string;
  price: string;
  image?: string;
  description?: string;
  rating?: number;
  discount?: string;
  availability?: string;
}

// Define response display types
type DisplayType =
  | "text"
  | "product_card"
  | "product_grid"
  | "comparison_table";

// Define message content structure
interface StructuredMessageContent {
  type: DisplayType;
  text: string;
  products?: ProductData[];
  comparisonAttributes?: string[];
}

// Standard content can be just a string
type MessageContent = string | StructuredMessageContent;

// Extended ChatMessage type to handle our display types
interface ExtendedChatMessage extends Omit<ChatMessage, "content"> {
  content: MessageContent;
}

export const ChatPreview = ({
  customization,
  onClose,
  chatbotId = "chatbot_A",
}: ChatPreviewProps) => {
  const [messages, setMessages] = useState<ExtendedChatMessage[]>([]);
  const [userInput, setUserInput] = useState("");
  const [isExpanded, setIsExpanded] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  // Initialize WebSocket connection
  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8090");
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connection established");
      setIsConnected(true);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("Received message from server:", data);

        // Stop typing animation
        setIsTyping(false);

        // Process the response based on the display type
        processResponse(data);
      } catch (error) {
        console.error("Error processing message:", error);
        setIsTyping(false);

        // Add error message to chat
        const errorMessage: ExtendedChatMessage = {
          id: Date.now().toString(),
          sender: "bot",
          content: "Sorry, I couldn't process that response. Please try again.",
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, errorMessage]);
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      setIsConnected(false);
    };

    socket.onclose = () => {
      console.log("WebSocket connection closed");
      setIsConnected(false);
    };

    // Clean up WebSocket connection when component unmounts
    return () => {
      if (
        socket.readyState === WebSocket.OPEN ||
        socket.readyState === WebSocket.CONNECTING
      ) {
        socket.close();
      }
    };
  }, []);

  const processResponse = (data: any) => {
    // Handle error responses
    if (data.status === "error") {
      const errorMessage: ExtendedChatMessage = {
        id: Date.now().toString(),
        sender: "bot",
        content: `Sorry, there was an error: ${data.message}`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      return;
    }

    // Create a new bot message based on the display type
    const botMessage: ExtendedChatMessage = {
      id: Date.now().toString(),
      sender: "bot",
      timestamp: new Date(),
      content: createMessageContent(data),
    };

    // Add the message to our chat
    setMessages((prev) => [...prev, botMessage]);
  };

  // Helper function to create appropriate message content based on display type
  const createMessageContent = (data: any): MessageContent => {
    const displayType = data.display_type || "text";
    const responseText = data.response || "I received your message.";

    console.log('data: ', data);

    switch (displayType) {
      case "text":
        return responseText;

      case "product_card":
        return {
          type: "product_card",
          text: responseText,
          products: data.products
            ? [data.products[0]]
            : [
                {
                  id: "1",
                  name: "Sample Product",
                  price: "$99.99",
                  image: "/api/placeholder/200/200",
                  description: "No product information available",
                },
              ],
        };

      case "product_grid":
        return {
          type: "product_grid",
          text: responseText,
          products: data.products || [
            {
              id: "1",
              name: "Sample Product 1",
              price: "$99.99",
              image: "/api/placeholder/200/200",
            },
            {
              id: "2",
              name: "Sample Product 2",
              price: "$129.99",
              image: "/api/placeholder/200/200",
            },
          ],
        };

      case "comparison_table":
        return {
          type: "comparison_table",
          text: responseText,
          products: data.products || [],
          comparisonAttributes: data.comparison_attributes || [
            "Price",
            "Rating",
            "Features",
          ],
        };

      default:
        return responseText;
    }
  };

  useEffect(() => {
    // Add welcome message when component mounts
    if (messages.length === 0) {
      setMessages([
        {
          id: Date.now().toString(),
          sender: "bot",
          content: customization.welcomeMessage,
          timestamp: new Date(),
        },
      ]);

      // Add predefined questions if available
      if (
        customization.predefinedQuestions &&
        customization.predefinedQuestions.length > 0
      ) {
        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now().toString(),
              sender: "bot",
              content: "Here are some questions you might want to ask:",
              timestamp: new Date(),
            },
          ]);
        }, 1000);
      }
    }
  }, [customization, messages.length]);

  useEffect(() => {
    // Scroll to bottom whenever messages change
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = () => {
    if (!userInput.trim()) return;

    // Add user message
    const userMessage: ExtendedChatMessage = {
      id: Date.now().toString(),
      sender: "user",
      content: userInput,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);

    // Start typing animation
    setIsTyping(true);

    // Send message to WebSocket if connected
    if (
      socketRef.current &&
      socketRef.current.readyState === WebSocket.OPEN &&
      isConnected
    ) {
      const messagePayload = {
        chatbot_id: chatbotId,
        query: userInput,
      };

      socketRef.current.send(JSON.stringify(messagePayload));
      console.log("Sent message to server:", messagePayload);
    } else {
      // Fallback if WebSocket is not connected
      setTimeout(() => {
        setIsTyping(false);

        const botResponse: ExtendedChatMessage = {
          id: Date.now().toString(),
          sender: "bot",
          content:
            "Sorry, I'm having trouble connecting to the server. Please try again later.",
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, botResponse]);
      }, 1500);
    }

    // Clear user input
    setUserInput("");
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  const getBubbleStyle = (sender: string) => {
    if (sender === "user") {
      return `bg-gray-100 text-gray-800 ml-auto rounded-t-lg rounded-bl-lg`;
    } else {
      const bgColor = customization.primaryColor || "#9b87f5";
      const bgColorClass = bgColor.startsWith("#") ? "" : bgColor;
      return `${bgColorClass} rounded-t-lg rounded-br-lg ${
        bgColorClass ? "" : "bg-chatbot-primary"
      } text-white`;
    }
  };

  // Get star rating display
  const renderStarRating = (rating: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      if (i <= rating) {
        stars.push(
          <span key={i} className="text-yellow-400">
            ★
          </span>
        );
      } else {
        stars.push(
          <span key={i} className="text-gray-300">
            ★
          </span>
        );
      }
    }
    return <div className="flex">{stars}</div>;
  };

  // Render different message content based on type
  const renderMessageContent = (content: MessageContent) => {
    if (typeof content === "string") {
      return <div className="whitespace-pre-wrap">{content}</div>;
    }

    // For complex content types
    switch (content.type) {
      case "product_card":
        const product = content.products?.[0];
        if (!product) return <div>{content.text}</div>;

        return (
          <div className="flex flex-col">
            <div className="mb-2">{content.text}</div>
            <div className="bg-white rounded-md overflow-hidden shadow-md">
              {product.image && (
                <div className="w-full h-40 bg-gray-100 flex items-center justify-center overflow-hidden">
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              <div className="p-3 text-gray-800">
                <div className="font-medium text-lg">{product.name}</div>
                <div className="flex justify-between items-center mt-1">
                  <div className="text-lg font-bold">{product.price}</div>
                  {product.discount && (
                    <div className="text-sm bg-red-500 text-white px-2 py-0.5 rounded">
                      {product.discount}
                    </div>
                  )}
                </div>
                {product.rating && (
                  <div className="mt-1">{renderStarRating(product.rating)}</div>
                )}
                {product.description && (
                  <div className="text-sm mt-2 text-gray-600">
                    {product.description}
                  </div>
                )}
                {product.availability && (
                  <div
                    className={`text-sm mt-2 ${
                      product.availability.toLowerCase().includes("stock")
                        ? "text-green-600"
                        : "text-red-600"
                    }`}
                  >
                    {product.availability}
                  </div>
                )}
                <Button className="w-full mt-3 text-white" size="sm">
                  View Details
                </Button>
              </div>
            </div>
          </div>
        );

      case "product_grid":
        if (!content.products || content.products.length === 0)
          return <div>{content.text}</div>;

        return (
          <div className="flex flex-col">
            <div className="mb-2">{content.text}</div>
            <div className="grid grid-cols-2 gap-2">
              {content.products.map((product, index)=> (
                <div
                  key={product.id || index}
                  className="bg-white rounded-md overflow-hidden shadow-sm"
                >
                  {product.image && (
                    <div className="w-full h-24 bg-gray-100 flex items-center justify-center overflow-hidden">
                      <img
                        src={product.image}
                        alt={product.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}
                  <div className="p-2 text-gray-800">
                    <div className="font-medium text-sm truncate">
                      {product.name}
                    </div>
                    <div className="flex justify-between items-center mt-1">
                      <div className="text-sm font-bold">{product.price}</div>
                      {product.rating && (
                        <div className="text-xs text-yellow-400">
                          {"★".repeat(Math.floor(product.rating))}
                          <span className="text-gray-300">
                            {"★".repeat(5 - Math.floor(product.rating))}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case "comparison_table":
        if (!content.products || content.products.length === 0)
          return <div>{content.text}</div>;

        return (
          <div className="flex flex-col">
            <div className="mb-2">{content.text}</div>
            <div className="bg-white rounded-md overflow-x-auto shadow-md">
              <table className="w-full text-left text-xs">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="p-2 border-b"></th>
                    {content.products.map((product, index)=> (
                      <th key={product.id || index} className="p-2 border-b">
                        <div className="font-medium">{product.name}</div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="text-gray-800">
                  {/* Product Images */}
                  <tr>
                    <td className="p-2 border-b font-medium">Image</td>
                    {content.products.map((product, index)=> (
                      <td key={`img-${product.id || index}`} className="p-2 border-b">
                        {product.image && (
                          <div className="w-16 h-16 bg-gray-100 flex items-center justify-center overflow-hidden mx-auto">
                            <img
                              src={product.image}
                              alt={product.name}
                              className="w-full h-full object-cover"
                            />
                          </div>
                        )}
                      </td>
                    ))}
                  </tr>

                  {/* Price Row */}
                  <tr className="bg-gray-50">
                    <td className="p-2 border-b font-medium">Price</td>
                    {content.products.map((product, index)=> (
                      <td
                        key={`price-${product.id || index}`}
                        className="p-2 border-b font-bold"
                      >
                        {product.price}
                      </td>
                    ))}
                  </tr>

                  {/* Rating Row */}
                  <tr>
                    <td className="p-2 border-b font-medium">Rating</td>
                    {content.products.map((product, index)=> (
                      <td key={`rating-${product.id || index}`} className="p-2 border-b">
                        {product.rating ? (
                          <div className="text-xs text-yellow-400">
                            {"★".repeat(Math.floor(product.rating))}
                            <span className="text-gray-300">
                              {"★".repeat(5 - Math.floor(product.rating))}
                            </span>
                          </div>
                        ) : (
                          "-"
                        )}
                      </td>
                    ))}
                  </tr>

                  {/* Availability Row */}
                  <tr className="bg-gray-50">
                    <td className="p-2 border-b font-medium">Availability</td>
                    {content.products.map((product, index)=> (
                      <td
                        key={`avail-${product.id || index}`}
                        className={`p-2 border-b ${
                          product.availability?.toLowerCase().includes("stock")
                            ? "text-green-600"
                            : "text-red-600"
                        }`}
                      >
                        {product.availability || "-"}
                      </td>
                    ))}
                  </tr>

                  {/* Description Row */}
                  <tr>
                    <td className="p-2 border-b font-medium">Description</td>
                    {content.products.map((product, index)=> (
                      <td
                        key={`desc-${product.id || index}`}
                        className="p-2 border-b text-xs"
                      >
                        {product.description || "-"}
                      </td>
                    ))}
                  </tr>

                  {/* Custom Attributes */}
                  {content.comparisonAttributes
                    ?.filter(
                      (attr) =>
                        ![
                          "price",
                          "rating",
                          "availability",
                          "description",
                        ].includes(attr.toLowerCase())
                    )
                    .map((attr, idx) => (
                      <tr
                        key={attr}
                        className={idx % 2 === 0 ? "bg-gray-50" : ""}
                      >
                        <td className="p-2 border-b font-medium">{attr}</td>
                        {content.products?.map((product, index)=> (
                          <td
                            key={`${attr}-${product.id || index}`}
                            className="p-2 border-b"
                          >
                            {(product as any)[attr.toLowerCase()] || "-"}
                          </td>
                        ))}
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        );

      default:
        return <div>{content.text}</div>;
    }
  };

  return (
    <div
      className={`fixed ${
        customization.position === "right" ? "right-5" : "left-5"
      } bottom-5 shadow-lg rounded-lg overflow-hidden flex flex-col z-50 transition-all duration-300 ease-in-out max-w-sm w-full`}
      style={{
        fontFamily:
          customization.font === "modern"
            ? "Inter, sans-serif"
            : customization.font === "classic"
            ? "Georgia, serif"
            : customization.font === "playful"
            ? "Comic Sans MS, cursive"
            : "system-ui, sans-serif",
        maxHeight: isExpanded ? "100vh" : "80px",
      }}
    >
      {/* Header */}
      <div
        className="p-3 flex justify-between items-center cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          backgroundColor: customization.primaryColor || "#9b87f5",
          color: "white",
        }}
      >
        <div className="flex items-center space-x-2">
          {customization.avatarUrl ? (
            <img
              src={customization.avatarUrl}
              alt={customization.name}
              className="w-8 h-8 rounded-full"
            />
          ) : (
            <MessageSquare className="w-6 h-6" />
          )}
          <span className="font-medium">
            {customization.name || "Chat Bot"}
          </span>
          {!isConnected && (
            <span className="text-xs text-red-200">(offline)</span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {isExpanded ? (
            <ChevronDown className="w-5 h-5" />
          ) : (
            <ChevronUp className="w-5 h-5" />
          )}
          <X
            className="w-5 h-5 cursor-pointer"
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
          />
        </div>
      </div>

      {/* Chat Area - Only shown when expanded */}
      {isExpanded && (
        <>
          <div className="bg-white flex-grow overflow-y-auto p-4 h-80">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.sender === "user" ? "justify-end" : "justify-start"
                } mb-3`}
              >
                <div
                  className={cn(
                    "max-w-[85%] p-3 animate-slide-in",
                    getBubbleStyle(message.sender),
                    customization.chatBubbleStyle === "sharp"
                      ? "rounded-none"
                      : "",
                    customization.chatBubbleStyle === "bubble"
                      ? "rounded-full"
                      : ""
                  )}
                  style={
                    message.sender === "bot" &&
                    customization.primaryColor?.startsWith("#")
                      ? {
                          backgroundColor: customization.primaryColor,
                        }
                      : {}
                  }
                >
                  {renderMessageContent(message.content)}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start mb-3">
                <div
                  className={cn(
                    "max-w-[80%] p-3",
                    getBubbleStyle("bot"),
                    customization.chatBubbleStyle === "sharp"
                      ? "rounded-none"
                      : "",
                    customization.chatBubbleStyle === "bubble"
                      ? "rounded-full"
                      : ""
                  )}
                  style={
                    customization.primaryColor?.startsWith("#")
                      ? {
                          backgroundColor: customization.primaryColor,
                        }
                      : {}
                  }
                >
                  <div className="flex space-x-1">
                    <div
                      className="w-2 h-2 bg-white rounded-full animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-white rounded-full animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-white rounded-full animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    ></div>
                  </div>
                </div>
              </div>
            )}

            {/* Predefined Questions */}
            {customization.predefinedQuestions &&
              customization.predefinedQuestions.length > 0 &&
              messages.length <= 2 && (
                <div className="mt-4 space-y-2">
                  {customization.predefinedQuestions.map((question, index) => (
                    <Button
                      key={`question-${index}`}
                      variant="outline"
                      className="text-left text-sm p-2 w-full justify-start"
                      onClick={() => {
                        setUserInput(question);
                        setTimeout(() => handleSendMessage(), 100);
                      }}
                    >
                      {question}
                    </Button>
                  ))}
                </div>
              )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-3 border-t flex items-center bg-white">
            <Input
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-grow mr-2"
              disabled={!isConnected}
            />
            <Button
              onClick={handleSendMessage}
              size="icon"
              disabled={!isConnected}
              style={{
                backgroundColor: customization.primaryColor || "#9b87f5",
              }}
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </>
      )}
    </div>
  );
};