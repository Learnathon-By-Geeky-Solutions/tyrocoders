import {
  Tag,
  Users,
  Settings,
  Bookmark,
  SquarePen,
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
          submenus: []
        }
      ]
    },
    {
      groupLabel: "Automation",
      menus: [
        {
          href: "",
          label: "Bots",
          icon: Bot,
          submenus: [
            {
              href: "/bots/viewbots",
              label: "My Bots"
            },
            {
              href: "/bots/setup",
              label: "Set-up"
            },
            {
              href: "/bots/widget",
              label: "Widget"
            }
          ]
        }
      ]
    },
    {
      groupLabel: "Collaboration",
      menus: [
        {
          href: "/teams",
          label: "Teams",
          icon: UsersRound
        }
      ]
    },
    {
      groupLabel: "Settings",
      menus: [
        {
          href: "/users",
          label: "Users",
          icon: Users
        },
        {
          href: "/account",
          label: "Account",
          icon: Settings
        }
      ]
    }
  ];
}
