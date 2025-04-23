import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { ScrollReveal } from "@/components/landing/ScrollReveal";

export function CtaSection() {
  return (
    <section className="bg-accent py-16">
      <ScrollReveal>
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Transform Your Customer Experience?
          </h2>
          <p className="text-white/90 text-lg md:text-xl mb-8 max-w-3xl mx-auto">
            Join thousands of businesses using ChatbotCreator to boost sales and
            provide 24/7 customer support.
          </p>
          <Button className="bg-white text-accent hover:bg-white/90 px-8 py-6 text-lg rounded-md shadow-lg transform transition-transform duration-200 hover:scale-105">
            Get Started Today <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      </ScrollReveal>
    </section>
  );
}
