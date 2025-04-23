import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";
import RootLayoutClient from "./RootLayoutClient";
import { Toaster } from "@/components/ui/toaster";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"],
  variable: "--font-poppins",
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
      <body className={poppins.variable}>
        <RootLayoutClient>{children}</RootLayoutClient>{" "}
        {/* Use Client Component */}
        <Toaster />
      </body>
    </html>
  );
}
