import { ChevronLeft } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useSidebar } from "@/hooks/use-sidebar"; // Import sidebar hook

interface SidebarToggleProps {
  isOpen: boolean | undefined;
  setIsOpen?: () => void;
}

export function SidebarToggle({ isOpen, setIsOpen }: SidebarToggleProps) {
  const sidebar = useSidebar();

  return (
    <div className="invisible lg:visible absolute top-[12px] -right-[16px] z-20">
      <Button
        onClick={() => {
          sidebar.toggleOpen(); // Toggle sidebar state
          // setIsOpen?.();
        }}
        className="bg-white h-7 w-7 text-dark rounded-full shadow-md shadow-black/30 hover:bg-gray-50 hover:text-dark"
        variant="custom"
        size="icon"
      >
        <ChevronLeft
          className={cn(
            "h-4 w-4 transition-transform ease-in-out duration-700",
            isOpen === false ? "rotate-180" : "rotate-0"
          )}
        />
      </Button>
    </div>
  );
}
