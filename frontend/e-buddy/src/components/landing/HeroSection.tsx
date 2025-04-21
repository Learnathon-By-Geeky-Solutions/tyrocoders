import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { ScrollReveal } from "@/components/landing/ScrollReveal";

export function HeroSection() {
  return (
    <section className="bg-white py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center gap-12">
        <ScrollReveal className="flex-1 text-center md:text-left">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
            Create <span className="text-vibrant">Smart Chatbots</span> That
            Grow Your Business
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl">
            Build AI-powered chatbots that boost sales, reduce support costs,
            and engage customers 24/7 - all without writing a single line of
            code.
          </p>
          <Button className="bg-vibrant hover:bg-vibrant/90 text-white px-8 py-6 text-lg rounded-md transform transition-transform duration-200 hover:scale-105">
            Get Started <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </ScrollReveal>
        <ScrollReveal className="flex-1">
          <div className="rounded-lg overflow-hidden shadow-xl border transition-transform duration-200 hover:shadow-2xl">
            <img
              src="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=600&h=450"
              alt="Chatbot in action"
              className="w-full h-auto"
            />
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
