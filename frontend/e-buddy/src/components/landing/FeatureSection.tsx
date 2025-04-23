import {
  MessageSquare,
  RefreshCw,
  Image,
  Mic,
  Star,
  Code,
  FileText,
  Settings,
  Clock,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollReveal } from "@/components/landing/ScrollReveal";

const features = [
  {
    icon: (
      <MessageSquare className="h-12 w-12 p-2 bg-chatbot-purple/10 text-chatbot-purple rounded-xl" />
    ),
    title: "Chat History",
    description:
      "Preserve context with comprehensive chat history for more personalized conversations",
  },
  {
    icon: (
      <RefreshCw className="h-12 w-12 p-2 bg-chatbot-blue/10 text-chatbot-blue rounded-xl" />
    ),
    title: "Auto-Update Knowledge Base",
    description:
      "Keep your chatbot up-to-date with self-learning capabilities that grow with your business",
  },
  {
    icon: (
      <Image className="h-12 w-12 p-2 bg-chatbot-purple/10 text-chatbot-purple rounded-xl" />
    ),
    title: "Image Search",
    description:
      "Enable visual search capabilities to help customers find exactly what they're looking for",
  },
  {
    icon: (
      <Mic className="h-12 w-12 p-2 bg-chatbot-orange/10 text-chatbot-orange rounded-xl" />
    ),
    title: "Voice Search",
    description:
      "Offer hands-free convenience with advanced voice recognition technology",
  },
  {
    icon: (
      <Star className="h-12 w-12 p-2 bg-chatbot-pink/10 text-chatbot-pink rounded-xl" />
    ),
    title: "Product Recommendations",
    description:
      "Increase sales with AI-powered personalized recommendations that delight customers",
  },
  {
    icon: (
      <Clock className="h-12 w-12 p-2 bg-chatbot-blue/10 text-chatbot-blue rounded-xl" />
    ),
    title: "Fast Creation",
    description: "Build and deploy your custom chatbot in minutes, not weeks",
  },
  {
    icon: (
      <Code className="h-12 w-12 p-2 bg-chatbot-orange/10 text-chatbot-orange rounded-xl" />
    ),
    title: "Embeddable Widget",
    description:
      "Seamlessly integrate your chatbot into any website with just a simple copy-paste",
  },
  {
    icon: (
      <Settings className="h-12 w-12 p-2 bg-chatbot-pink/10 text-chatbot-pink rounded-xl" />
    ),
    title: "Easy Customization",
    description:
      "Match your brand perfectly with simple yet powerful customization tools",
  },
];

export function FeaturesSection() {
  return (
    <section className="section bg-gray-50 py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="section-title">
          Powerful Features <span className="text-accent">You'll Love</span>
        </h2>
        <p className="section-subtitle">
          Everything you need to create intelligent, engaging, and
          conversion-focused chatbots
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <ScrollReveal key={index}>
              <Card className="border border-border feature-card h-full">
                <CardHeader className="pb-2">
                  <div className="mb-4">{feature.icon}</div>
                  <CardTitle className="text-lg font-semibold">
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-muted-foreground">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}
