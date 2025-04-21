import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { ScrollReveal } from "@/components/landing/ScrollReveal";

const faqItems = [
  {
    question: "How long does it take to create a chatbot?",
    answer:
      "With our platform, you can create a fully functioning chatbot in as little as 10 minutes. Just upload your knowledge base, customize the appearance to match your brand, and generate the embed code to add to your website.",
  },
  {
    question: "Do I need technical skills to create a chatbot?",
    answer:
      "Not at all! Our platform is designed for non-technical users. The intuitive interface guides you through each step of the process with no coding required. If you can use a web browser, you can create a chatbot.",
  },
  {
    question: "How does the chatbot learn about my business?",
    answer:
      "You can train your chatbot by uploading existing documents (PDFs, Word files, etc.), connecting to your knowledge base, or letting our system automatically scan your website. The AI will extract the relevant information and use it to answer customer questions accurately.",
  },
  {
    question: "Can I customize how the chatbot looks?",
    answer:
      "Absolutely! You can customize colors, fonts, button styles, chat bubble shapes, and even add your logo. Our visual editor makes it easy to ensure your chatbot perfectly matches your brand identity.",
  },
  {
    question: "What happens if the chatbot can't answer a question?",
    answer:
      "You can set up fallback options such as connecting to live chat, creating a support ticket, or collecting contact information. The system can also learn from these instances to improve future responses.",
  },
  {
    question: "Can I integrate the chatbot with other tools?",
    answer:
      "Yes! Our chatbot integrates with popular CRM systems, help desks, email marketing platforms, and more. This allows for seamless data flow between your chatbot and existing business tools.",
  },
  {
    question: "How does billing work for conversations?",
    answer:
      "A 'conversation' is defined as a complete interaction with a visitor, regardless of how many messages are exchanged. Our plans include a set number of monthly conversations, and you can always upgrade if you need more.",
  },
  {
    question: "Is there a way to test my chatbot before making it live?",
    answer:
      "Yes, you can use our preview mode to test your chatbot thoroughly before publishing it. This allows you to interact with it exactly as your customers would, making sure everything works perfectly.",
  },
];

export function FaqSection() {
  return (
    <section className="section bg-white py-16 md:py-24">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <ScrollReveal>
          <h2 className="section-title">
            Frequently Asked <span className="text-vibrant">Questions</span>
          </h2>
          <p className="section-subtitle">
            Everything you need to know about our chatbot platform
          </p>
        </ScrollReveal>

        <ScrollReveal>
          <Accordion type="single" collapsible className="mt-8">
            {faqItems.map((item, index) => (
              <AccordionItem
                key={index}
                value={`item-${index}`}
                className="border-b"
              >
                <AccordionTrigger className="text-left font-medium py-4">
                  {item.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground pb-4">
                  {item.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </ScrollReveal>
      </div>
    </section>
  );
}
