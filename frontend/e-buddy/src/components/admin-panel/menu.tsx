"use client";

import Link from "next/link";
import { Ellipsis, LogOut } from "lucide-react";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";
import { getMenuList } from "@/lib/menu-list";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CollapseMenuButton } from "@/components/admin-panel/collapse-menu-button";
import { useAuth } from "@/context/AuthContext";

interface MenuProps {
  isOpen: boolean | undefined;
}

export function Menu({ isOpen }: MenuProps) {
  const pathname = usePathname();
  const menuList = getMenuList(pathname);

  const { isAuthenticated, user, logout } = useAuth();

  return (
    <aside className="w-64 text-[#A0A0A0]">
      <ScrollArea className="h-full">
        <nav className="mt-6">
          <ul className="space-y-1">
            {menuList.map(({ groupLabel, menus }, groupIdx) => (
              <li key={groupIdx}>
                {isOpen && groupLabel && (
                  <p className="px-4 pb-2 text-xs font-semibold uppercase text-gray-500">
                    {groupLabel}
                  </p>
                )}

                {menus.map(
                  ({ href, label, icon: Icon, active, submenus }, idx) => {
                    const isActive =
                      active === undefined ? pathname.startsWith(href) : active;

                    if (!submenus || submenus.length === 0) {
                      return (
                        <Link
                          key={idx}
                          href={href}
                          className={cn(
                            "flex items-center px-3 py-2 w-full transition-colors duration-200",
                            isActive
                              ? "bg-accent border-l-2 text-white"
                              : "hover:bg-accent2-light hover:text-white"
                          )}
                        >
                          <Icon className="h-5 w-5 flex-shrink-0" />
                          {isOpen !== false && (
                            <>
                              <span className="ml-3 flex-1 truncate">
                                {label}
                              </span>
                            </>
                          )}
                          {!isOpen && !isActive && (
                            <span className="sr-only">{label}</span>
                          )}
                        </Link>
                      );
                    }

                    return (
                      <CollapseMenuButton
                        key={idx}
                        icon={Icon}
                        label={label}
                        active={isActive}
                        submenus={submenus}
                        isOpen={isOpen}
                      />
                    );
                  }
                )}
              </li>
            ))}

            {/* Logout Button */}
            <li className="mt-6">
              <button
                onClick={logout}
                className="flex items-center w-full px-3 py-2 hover:bg-accent2-light hover:text-white transition-colors duration-200"
              >
                <LogOut className="h-5 w-5" />
                {isOpen !== false && <span className="ml-3">Sign out</span>}
                {isOpen === false && <span className="sr-only">Sign out</span>}
              </button>
            </li>
          </ul>
        </nav>
      </ScrollArea>
    </aside>
  );
}
