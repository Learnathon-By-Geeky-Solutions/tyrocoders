"use client";

import { usePathname } from "next/navigation";
import Navbar from "../components/Navbar";

export default function RootLayoutClient({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  console.log("Current Path:", pathname);

  const isDemoPage =
    pathname.startsWith("/dashboard") ||
    pathname.startsWith("/users") ||
    pathname.startsWith("/bots") ||
    pathname.startsWith("/settings");

  return (
    <>
      {!isDemoPage && <Navbar />}
      {children}
    </>
  );
}
