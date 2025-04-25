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

  const isLandingPage = pathname === "/";

  return (
    <AuthProvider>
      {isLandingPage && <Navbar />}
      {children}
    </AuthProvider>
  );
}
