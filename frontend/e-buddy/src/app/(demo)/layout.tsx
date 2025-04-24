"use client";

import AdminPanelLayout from "@/components/admin-panel/admin-panel-layout";
import { ThemeProvider } from "@/context/ThemeContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/context/AuthContext"; // assuming this is your auth context

export default function DemoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth(); // get auth state

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push("/auth"); // redirect to login if not authenticated
    }
  }, [isAuthenticated, loading, router]);

  if (loading || !isAuthenticated) {
    // optionally show a loading spinner or nothing
    return null;
  }

  return (
    <ThemeProvider>
      <AdminPanelLayout>{children}</AdminPanelLayout>
    </ThemeProvider>
  );
}
