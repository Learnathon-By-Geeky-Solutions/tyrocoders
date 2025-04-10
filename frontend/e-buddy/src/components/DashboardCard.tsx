import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Bot, FileText, FileStack, HelpCircle, ArrowUpRight, Activity, Users, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

type StatCardProps = {
  icon: React.ElementType;
  title: string;
  count: number;
  link: string;
  className?: string;
  trend?: number;
};

const StatCard = ({ icon: Icon, title, count, link, className, trend }: StatCardProps) => (
  <a href={link} className="group block">
    <Card className={cn(
      "overflow-hidden border-none bg-white/80 backdrop-blur-sm rounded-xl shadow-md hover:shadow-xl transition-all duration-300 h-full", 
      className
    )}>
      <div className="absolute top-0 right-0 w-20 h-20 opacity-10 transform translate-x-6 -translate-y-6">
        <Icon className="w-full h-full" />
      </div>
      <CardContent className="p-6">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
            <Icon className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <h3 className="text-2xl font-bold text-gray-800 mt-1">{count}</h3>
          </div>
        </div>
        
        {trend !== undefined && (
          <div className="mt-4 flex items-center">
            <span className={cn(
              "text-xs font-medium",
              trend > 0 ? "text-green-500" : "text-red-500"
            )}>
              {trend > 0 ? "+" : ""}{trend}%
            </span>
            <span className="text-xs text-gray-500 ml-2">from last month</span>
          </div>
        )}
      </CardContent>
    </Card>
  </a>
);

type FeatureCardProps = {
  icon: React.ElementType;
  title: string;
  description: string;
  link: string;
  className?: string;
};

const FeatureCard = ({ icon: Icon, title, description, link, className }: FeatureCardProps) => (
  <a href={link} className="group block">
    <Card className={cn(
      "border-none bg-white/80 backdrop-blur-sm rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden h-full",
      className
    )}>
      <div className="absolute top-0 right-0 w-32 h-32 opacity-5 transform translate-x-8 -translate-y-8">
        <Icon className="w-full h-full" />
      </div>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
            <Icon className="w-5 h-5" />
          </div>
          <CardTitle className="text-xl font-bold text-gray-800">{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-gray-600">{description}</p>
        <div className="flex justify-end mt-4">
          <span className="text-blue-600 flex items-center gap-1 text-sm font-medium group-hover:text-blue-800 transition-colors">
            Learn more <ArrowUpRight className="w-4 h-4" />
          </span>
        </div>
      </CardContent>
    </Card>
  </a>
);

export function DashboardCards() {
  return (
    <div className="space-y-8">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          icon={Bot} 
          title="Total Bots" 
          count={12} 
          link="/bots" 
          trend={8}
        />
        <StatCard 
          icon={FileStack} 
          title="Knowledge Sources" 
          count={34} 
          link="/sources" 
          trend={12}
        />
        <StatCard 
          icon={FileText} 
          title="Pages Created" 
          count={56} 
          link="/pages" 
          trend={-3}
        />
        <StatCard 
          icon={HelpCircle} 
          title="User Questions" 
          count={78} 
          link="/questions" 
          trend={24}
        />
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard 
            icon={Bot} 
            title="Manage Bots" 
            description="View, edit and monitor your AI bot performance and analytics." 
            link="/bots/viewbots" 
          />
          <FeatureCard 
            icon={Activity} 
            title="Train Bots" 
            description="Improve accuracy with custom training and fine-tuning." 
            link="/bots/train" 
          />
          <FeatureCard 
            icon={Users} 
            title="Teams & Collaboration" 
            description="Invite team members and manage collaboration settings." 
            link="/teams" 
          />
        </div>
      </div>

      {/* Additional Resources */}
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-4">Resources & Settings</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <FeatureCard 
            icon={Settings} 
            title="Plan & Billing" 
            description="Manage your subscription, usage limits and payment methods." 
            link="/billing" 
            className="bg-gradient-to-br from-white to-blue-50"
          />
          <FeatureCard 
            icon={HelpCircle} 
            title="Help & Documentation" 
            description="Tutorials, guides and support resources for getting started." 
            link="/docs" 
            className="bg-gradient-to-br from-white to-indigo-50"
          />
        </div>
      </div>
    </div>
  );
}
