import {
  Users,
  Settings,
  LayoutGrid,
  LucideIcon,
  Bot,
  UsersRound
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
          href: "/bots/viewbots",
          label: "My Bots",
          icon: Bot,
        },
        {
          href: "/bots/setup",
          label: "Set-up",
          icon: Bot,
        },
        {
          href: "/bots/chat",
          label: "Chat",
          icon: Bot,
        },
        {
          href: "/bots/widget",
          label: "Widget",
          icon: Bot,
        },
        {
          href: "/teams",
          label: "Teams",
          icon: UsersRound,
        },
        {
          href: "/users",
          label: "Users",
          icon: Users,
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