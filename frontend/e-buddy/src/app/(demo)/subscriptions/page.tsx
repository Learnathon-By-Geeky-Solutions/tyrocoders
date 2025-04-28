import Link from "next/link";

import PlaceholderContent from "@/components/demo/placeholder-content";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator
} from "@/components/ui/breadcrumb";


import { PlanCard } from "@/components/PlanCard";
import { AddonCard } from "@/components/AddonCard";


const Subscription = () => {
  return (
    
    <ContentLayout title="Subscriptions">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link href="/">Home</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link href="/dashboard">Dashboard</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Subscriptions</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
    

    <div className="min-h-screen py-8 bg-gradient-to-b to-white">
      
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-3xl">
            Choose Your <span className="text-accent">Perfect Plan</span>
          </h1>
          <div className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto -mb-8">
            Find the ideal package that fits your needs and unlock the full potential of our platform
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-16">
          <PlanCard
            name="Free"
            monthlyPrice="0"
            description="Perfect for individuals just getting started"
            features={[
              { name: "Chatbot Limit:", included: true, value: "1" },
              { name: "Monthly Message Limit:", included: true, value: "100" },
              { name: "Character Training Limit:", included: true, value: "5,000" },
            ]}
            models={["GPT-3.5"]}
            supportLevel="Email Only"
          />
          
          <PlanCard
            name="Starter"
            monthlyPrice="9.99"
            yearlyPrice="99.99"
            description="Great for small projects and teams"
            features={[
              { name: "Chatbot Limit:", included: true, value: "3" },
              { name: "Monthly Message Limit:", included: true, value: "1,000" },
              { name: "Character Training Limit:", included: true, value: "25,000" },
            ]}
            models={["GPT-3.5", "GPT-4"]}
            supportLevel="Email & Chat"
          />
          
          <PlanCard
            name="Pro"
            monthlyPrice="29.99"
            yearlyPrice="299.99"
            description="Advanced features for businesses"
            features={[
              { name: "Chatbot Limit:", included: true, value: "10" },
              { name: "Monthly Message Limit:", included: true, value: "5,000" },
              { name: "Character Training Limit:", included: true, value: "100,000" },
            ]}
            models={["GPT-3.5", "GPT-4", "Claude"]}
            supportLevel="Priority Support"
            isPrimary={true}
            isPopular={true}
          />
          
          <PlanCard
            name="Enterprise"
            monthlyPrice="99.99"
            yearlyPrice="999.99"
            description="Full-scale solution for large organizations"
            features={[
              { name: "Chatbot Limit:", included: true, value: "Unlimited" },
              { name: "Monthly Message Limit:", included: true, value: "25,000" },
              { name: "Character Training Limit:", included: true, value: "Unlimited" },
            ]}
            models={["GPT-3.5", "GPT-4", "Claude", "DALL-E", "Anthropic"]}
            supportLevel="Dedicated Manager"
          />
        </div>

        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-gray-900">
              Enhance Your <span className="text-accent">Plan</span>
            </h2>
            <p className="mt-3 text-gray-600">
              Customize your subscription with these additional options
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <AddonCard
              name="Additional Chatbots"
              price={7.99}
              description="Add more chatbots to your account to handle different tasks or audiences"
              tiers={[
                { plan: "Free", quantity: "N/A" },
                { plan: "Starter", quantity: "2 max" },
                { plan: "Pro", quantity: "5 max" },
                { plan: "Enterprise", quantity: "∞" },
              ]}
            />
            
            <AddonCard
              name="Extra Messages"
              price={4.99}
              description="Increase your monthly message allowance per 1,000 additional messages"
              tiers={[
                { plan: "Free", quantity: "N/A" },
                { plan: "Starter", quantity: "1,000 max" },
                { plan: "Pro", quantity: "10,000 max" },
                { plan: "Enterprise", quantity: "∞" },
              ]}
            />
          </div>
        </div>
        
        <div className="mt-16 text-center">
          <p className="text-gray-600">
            Need help choosing the right plan? <a href="#" className="text-orange-600 font-medium hover:underline">Contact our sales team</a>
          </p>
        </div>
      </div>
    </div>
    </ContentLayout>
  );
};

export default Subscription;
