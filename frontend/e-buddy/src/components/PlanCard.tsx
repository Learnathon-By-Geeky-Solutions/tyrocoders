import { Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";

interface PlanFeature {
  name: string;
  included: boolean;
  value?: string | number;
}

interface PlanProps {
  name: string;
  monthlyPrice: number | string;
  yearlyPrice?: number | string;
  description: string;
  features: PlanFeature[];
  models: string[];
  supportLevel: string;
  isPrimary?: boolean;
  isPopular?: boolean;
}

export function PlanCard({
  name,
  monthlyPrice,
  yearlyPrice,
  description,
  features,
  models,
  supportLevel,
  isPrimary = false,
  isPopular = false,
}: PlanProps) {
  return (
    <Card className={`pricing-card w-full ${isPrimary ? 'border-2 border-orange-500 relative' : ''}`}>
      {isPopular && (
        <div className="absolute top-0 right-0 transform translate-x-1/4 -translate-y-1/4">
          <div className="bg-orange-600 text-white text-xs font-semibold px-3 py-1 rounded-full shadow-md">
            Popular
          </div>
        </div>
      )}
      
      <CardHeader className={`pb-3 ${isPrimary ? 'bg-orange-50' : ''}`}>
        <h3 className="text-xl font-bold text-gray-900">{name}</h3>
        <div className="mt-1">
          <span className="text-3xl font-bold text-orange-600">${monthlyPrice}</span>
          <span className="text-gray-500 text-sm ml-1">/month</span>
        </div>
        {yearlyPrice && (
          <div className="text-sm text-gray-500 mt-1">
            ${yearlyPrice}/year <span className="text-orange-500">(Save 20%)</span>
          </div>
        )}
        <p className="text-gray-600 text-sm mt-2">{description}</p>
      </CardHeader>
      
      <CardContent className="pt-4">
        <ul className="space-y-3">
          {features.map((feature, index) => (
            <li key={index} className="flex items-start">
              {feature.included ? (
                <Check className="h-5 w-5 text-orange-500 flex-shrink-0 mr-2" />
              ) : (
                <span className="h-5 w-5 flex-shrink-0 mr-2">-</span>
              )}
              <span className="text-gray-700">
                {feature.name}
                {feature.value && <span className="font-medium ml-1">{feature.value}</span>}
              </span>
            </li>
          ))}
          
          <li className="flex flex-col gap-1">
            <div className="flex items-start">
              <Check className="h-5 w-5 text-orange-500 flex-shrink-0 mr-2" />
              <span className="text-gray-700">Models Available:</span>
            </div>
            <div className="ml-7 flex flex-wrap gap-1.5">
              {models.map((model, index) => (
                <Badge key={index} variant="outline" className="badge-pill">
                  {model}
                </Badge>
              ))}
            </div>
          </li>
          
          <li className="flex items-start">
            <Check className="h-5 w-5 text-orange-500 flex-shrink-0 mr-2" />
            <span className="text-gray-700">
              Support Level: <span className="font-medium">{supportLevel}</span>
            </span>
          </li>
        </ul>
      </CardContent>
      
      <CardFooter className="border-t bg-gray-50/50 pt-4 pb-6">
        <Button 
          className={`w-full ${isPrimary ? 'bg-orange-600 hover:bg-orange-700' : 'bg-orange-500 hover:bg-orange-600'}`}
        >
          Choose {name}
        </Button>
      </CardFooter>
    </Card>
  );
}
