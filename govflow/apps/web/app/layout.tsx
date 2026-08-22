import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "GovFlow AI - Universal Government Service Browser Agent",
  description: "AI-powered browser agent that helps citizens interact with government services through real government websites",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} antialiased`}>
      <body className="min-h-screen bg-slate-50 dark:bg-slate-900">
        {children}
      </body>
    </html>
  );
}