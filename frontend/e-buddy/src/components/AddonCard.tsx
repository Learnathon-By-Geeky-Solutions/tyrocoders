import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface AddonTier {
  plan: string;
  quantity: string | number;
}

interface AddonProps {
  name: string;
  price: number;
  description: string;
  tiers: AddonTier[];
}

export function AddonCard({ name, price, description, tiers }: AddonProps) {
  return (
    <Card className="pricing-card overflow-hidden">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-bold text-gray-900">{name}</h3>
            <p className="text-sm text-gray-600 mt-1">{description}</p>
          </div>
          <div className="text-right">
            <span className="text-xl font-bold text-accent">${price}</span>
            <span className="text-gray-500 text-sm ml-1">each</span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-2">
        <div className="flex flex-wrap gap-2 mt-2 justify-center">
          {tiers.map((tier, index) => (
            <div key={index} className="flex flex-col items-center bg-orange-50 border border-orange-100 px-2 py-2 rounded-lg">
              <span className="text-sm font-medium text-gray-700">{tier.plan}</span>
              <Badge variant="secondary" className="mt-1 bg-orange-100 text-accent hover:bg-orange-200">
                {tier.quantity}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
