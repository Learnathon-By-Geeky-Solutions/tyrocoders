import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { ScrollReveal } from "@/components/landing/ScrollReveal";

export function HeroSection() {
  return (
    <section className="bg-white py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center gap-12">
        <ScrollReveal className="flex-1 text-center md:text-left">
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight mb-6">
            Create <span className="text-accent">Smart Chatbots</span> That Grow
            Your Business
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl">
            Build AI-powered chatbots that boost sales, reduce support costs,
            and engage customers 24/7 - all without writing a single line of
            code.
          </p>
          <Button className="bg-accent hover:bg-accent/90 text-white px-8 py-6 text-lg rounded-md transform transition-transform duration-200 hover:scale-105">
            Get Started <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </ScrollReveal>
        <ScrollReveal className="flex-1">
          <div className="rounded-lg overflow-hidden shadow-xl border transition-transform duration-200 hover:shadow-2xl">
            <img
              src="https://www.livechat.com/images/homepage/product-view--desktop_hu4cbfe34f2a228990920ce661de5d9cce_538742_2240x0_resize_q75_h2_catmullrom_3.67a10e85bd853d692610504d1118097fea06ce0825b2597940e8632347c898d9.webp"
              // src="https://blog.getmanifest.ai/content/images/size/w1000/2023/07/Live-chat.jpg"
              alt="Chatbot in action"
              className="w-full h-auto"
            />
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
