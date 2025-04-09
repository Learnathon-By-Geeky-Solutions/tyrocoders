import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import "./globals.css";
import RootLayoutClient from "./RootLayoutClient";
import { Toaster } from "@/components/ui/toaster";

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["100", "200", "300", "400", "500", "600", "700", "800"],
  variable: "--font-jetbrainsMono",
});

export const metadata: Metadata = {
  title: "ebuddy",
  description: "Plug and play chatbot for ecommerce",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={jetbrainsMono.variable}>
        <RootLayoutClient>{children}</RootLayoutClient>{" "}
        {/* Use Client Component */}
        <Toaster />
      </body>
    </html>
  );
}
