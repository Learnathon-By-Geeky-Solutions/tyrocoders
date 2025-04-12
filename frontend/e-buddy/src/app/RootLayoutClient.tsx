"use client";

import { usePathname } from "next/navigation";
import Navbar from "../components/Navbar";
import { AuthProvider } from "@/context/AuthContext";

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
    <AuthProvider>
      {!isDemoPage && <Navbar />}
      {children}
    </AuthProvider>
  );
}
