import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import { ScrollReveal } from "@/components/landing/ScrollReveal";

const pricingPlans = [
  {
    name: "Starter",
    price: "$29",
    period: "/month",
    description:
      "Perfect for small businesses just getting started with chatbots",
    features: [
      "1 Chatbot",
      "500 monthly conversations",
      "Basic customization",
      "Standard response time",
      "Email support",
    ],
    buttonText: "Get Started",
    popular: false,
  },
  {
    name: "Professional",
    price: "$79",
    period: "/month",
    description:
      "Ideal for growing businesses that need more advanced features",
    features: [
      "3 Chatbots",
      "2,000 monthly conversations",
      "Advanced customization",
      "Fast response time",
      "Chat & email support",
      "Analytics dashboard",
      "Integration with CRM",
    ],
    buttonText: "Get Started",
    popular: true,
  },
  {
    name: "Business",
    price: "$149",
    period: "/month",
    description: "For businesses with high volume support and sales needs",
    features: [
      "10 Chatbots",
      "10,000 monthly conversations",
      "Full customization suite",
      "Lightning-fast responses",
      "Priority support",
      "Advanced analytics",
      "All integrations",
      "Multi-language support",
    ],
    buttonText: "Get Started",
    popular: false,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description:
      "Tailored solutions for large organizations with unique requirements",
    features: [
      "Unlimited chatbots",
      "Unlimited conversations",
      "Custom training & onboarding",
      "Dedicated account manager",
      "Custom integrations",
      "SLA guarantees",
      "White-label options",
      "On-premises deployment",
    ],
    buttonText: "Contact Us",
    popular: false,
  },
];

export function PricingSection() {
  return (
    <section className="section bg-gray-50 py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <ScrollReveal>
          <h2 className="section-title">
            Simple <span className="text-accent">Pricing</span>
          </h2>
          <p className="section-subtitle">
            Choose the perfect plan for your business needs
          </p>
        </ScrollReveal>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mt-12">
          {pricingPlans.map((plan, index) => (
            <ScrollReveal key={index}>
              <div
                className={`bg-white rounded-xl border ${
                  plan.popular
                    ? "border-accent ring-2 ring-accent/20"
                    : "border-border"
                } overflow-hidden transition-all shadow-sm hover:shadow-md h-full`}
              >
                {plan.popular && (
                  <div className="bg-accent text-white text-center py-1 text-sm font-medium">
                    Most Popular
                  </div>
                )}

                <div className="p-6">
                  <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                  <div className="mb-4">
                    <span className="text-3xl font-bold">{plan.price}</span>
                    <span className="text-muted-foreground">{plan.period}</span>
                  </div>
                  <p className="text-muted-foreground mb-6 text-sm">
                    {plan.description}
                  </p>

                  <Button
                    className={`w-full mb-6 ${
                      plan.popular ? "bg-accent hover:bg-accent/90" : ""
                    }`}
                    variant={plan.popular ? "default" : "outline"}
                  >
                    {plan.buttonText}
                  </Button>

                  <ul className="space-y-3">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start">
                        <Check className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}
