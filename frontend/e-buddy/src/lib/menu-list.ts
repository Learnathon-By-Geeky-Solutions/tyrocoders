import {
  Tag,
  Settings,
  MessageSquareText,
  LayoutGrid,
  Bot,
  LucideIcon,
} from "lucide-react";

type Submenu = {
  href: string;
  label: string;
  active?: boolean;
};

type Menu = {
  href: string;
  label: string;
  active?: boolean;
  icon: LucideIcon;
  submenus?: Submenu[];
};

type Group = {
  groupLabel: string;
  menus: Menu[];
};

export function getMenuList(pathname: string): Group[] {
  return [
    {
      groupLabel: "",
      menus: [
        {
          href: "/dashboard",
          label: "Dashboard",
          icon: LayoutGrid,
        },
        {
          href: "/bots/view",
          label: "Bots",
          icon: Bot,
        },
        {
          href: "/conversations",
          label: "Conversations",
          icon: MessageSquareText,
        },
        {
          href: "/subscriptions",
          label: "Subscriptions",
          icon: Tag,
        },
        {
          href: "/settings",
          label: "Settings",
          icon: Settings,
        },
      ],
    },
  ];
}
