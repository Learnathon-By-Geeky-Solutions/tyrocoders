import { FileText, Settings, Code, MessageSquare } from "lucide-react";
import { ScrollReveal } from "@/components/landing/ScrollReveal";

const steps = [
  {
    icon: (
      <FileText className="h-14 w-14 p-3 bg-chatbot-blue/10 text-chatbot-blue rounded-full" />
    ),
    title: "Train Your Chatbot",
    description:
      "Upload existing documents or let us scrape your website to build your knowledge base in seconds.",
  },
  {
    icon: (
      <Settings className="h-14 w-14 p-3 bg-chatbot-purple/10 text-chatbot-purple rounded-full" />
    ),
    title: "Customize Appearance",
    description:
      "Match your brand's colors, fonts, and style with our simple visual customizer.",
  },
  {
    icon: (
      <Code className="h-14 w-14 p-3 bg-chatbot-orange/10 text-chatbot-orange rounded-full" />
    ),
    title: "Generate Embed Code",
    description:
      "Get your unique embed code to place on your website with a simple copy and paste.",
  },
  {
    icon: (
      <MessageSquare className="h-14 w-14 p-3 bg-chatbot-pink/10 text-chatbot-pink rounded-full" />
    ),
    title: "Go Live!",
    description:
      "Your intelligent chatbot is ready to engage visitors and provide 24/7 support.",
  },
];

export function HowItWorksSection() {
  return (
    <section className="section bg-white py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <ScrollReveal>
          <h2 className="section-title">
            How It <span className="text-vibrant">Works</span>
          </h2>
          <p className="section-subtitle">
            Create your custom AI chatbot in four simple steps
          </p>
        </ScrollReveal>

        <div className="relative mt-12">
          {/* Connecting line */}
          <div className="absolute left-1/2 transform -translate-x-1/2 h-full w-1 bg-gray-100 hidden md:block" />

          <div className="space-y-12 md:space-y-0">
            {steps.map((step, index) => (
              <ScrollReveal key={index}>
                <div className="relative flex flex-col md:flex-row items-center">
                  <div
                    className={`w-full md:w-1/2 ${
                      index % 2 === 0
                        ? "md:pr-16 text-right"
                        : "md:pl-16 md:order-2"
                    }`}
                  >
                    <div
                      className={`p-6 bg-white rounded-lg shadow-sm border ${
                        index % 2 === 0 ? "md:ml-auto" : ""
                      }`}
                    >
                      <h3 className="text-xl font-semibold mb-2">
                        {step.title}
                      </h3>
                      <p className="text-muted-foreground">
                        {step.description}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-center my-4 md:my-0 md:absolute md:left-1/2 md:transform md:-translate-x-1/2 z-10">
                    <div className="h-16 w-16 rounded-full bg-white border-4 border-gray-100 flex items-center justify-center">
                      <span className="text-xl font-bold text-vibrant">
                        {index + 1}
                      </span>
                    </div>
                  </div>

                  <div
                    className={`hidden md:block w-1/2 ${
                      index % 2 === 0 ? "md:order-2" : "md:pr-16"
                    }`}
                  >
                    <div className="flex justify-center">{step.icon}</div>
                  </div>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
