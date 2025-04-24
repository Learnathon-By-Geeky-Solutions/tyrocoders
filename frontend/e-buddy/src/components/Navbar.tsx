"use client";

import { useState } from "react";
import { Menu, X } from "lucide-react";
import { Button } from "./ui/button";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { CiMenuFries } from "react-icons/ci";

const Navbar = () => {
  const pathname = usePathname();

  const links = [
    {
      name: "Home",
      path: "/",
    },
    {
      name: "Feature",
      path: "/feature",
    },
    {
      name: "Pricing",
      path: "/pricing",
    },
    {
      name: "FAQ",
      path: "/faq",
    },
  ];

  return (
    <header className="py-8 text-white">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/">
          <h1 className="text-4xl font-semibold">
            <span className="text-accent">e</span>buddy
          </h1>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden xl:flex lg:flex gap-12">
          <nav className="flex gap-8">
            {links.map((link, index) => {
              return (
                <Link
                  href={link.path}
                  key={index}
                  className={`${
                    link.path === pathname &&
                    "text-accent border-b-2 border-accent"
                  } flex items-center capitalize font-medium hover:text-accent transition-all`}
                >
                  {link.name}
                </Link>
              );
            })}
          </nav>
          <Link href="/auth">
            <Button variant="custom">Sign in</Button>
          </Link>
        </div>

        {/* Mobile Navigation */}
        <div className="xl:hidden lg:hidden">
          <Sheet>
            <SheetTrigger className="flex justify-center items-center">
              <CiMenuFries className="text-[32px] text-accent" />
            </SheetTrigger>
            <SheetContent className="flex flex-col text-white">
              <SheetTitle className="hidden">Menu</SheetTitle>
              <div className="mt-32 mb-24 text-center text-2xl">
                <Link href="/">
                  <h1 className="text-4xl font-semibold">
                    <span className="text-accent">e</span>buddy
                  </h1>
                </Link>
              </div>
              <nav className="flex flex-col justify-center items-center gap-4">
                {links.map((link, index) => {
                  return (
                    <Link
                      href={link.path}
                      key={index}
                      className={`${
                        link.path === pathname &&
                        "text-accent border-b-2 border-accent"
                      } flex items-center capitalize font-medium hover:text-accent transition-all`}
                    >
                      {link.name}
                    </Link>
                  );
                })}
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
