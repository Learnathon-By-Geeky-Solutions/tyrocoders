import { Button } from "@/components/ui/button";

export function Header() {
  return (
    <header className="border-b py-3 px-4 md:px-8 sticky top-0 bg-background z-50">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="flex items-center">
          <h1 className="text-xl font-bold text-vibrant">ChatbotCreator</h1>
        </div>

        <div className="hidden md:flex items-center space-x-6">
          <a
            href="#features"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Features
          </a>
          <a
            href="#how-it-works"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            How It Works
          </a>
          <a
            href="#pricing"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Pricing
          </a>
          <a
            href="#faq"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            FAQ
          </a>
        </div>

        <nav>
          <Button variant="ghost" className="font-medium">
            Login
          </Button>
          <Button className="ml-2 bg-vibrant hover:bg-vibrant/90 text-white">
            Sign Up
          </Button>
        </nav>
      </div>
    </header>
  );
}
