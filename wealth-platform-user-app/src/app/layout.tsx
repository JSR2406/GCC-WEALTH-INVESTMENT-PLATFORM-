import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GCC Wealth Platform",
  description: "Cross-border wealth management for the Gulf region",
  keywords: ["wealth management", "investment", "UAE", "Saudi Arabia", "portfolio", "goals"],
  authors: [{ name: "GCC Wealth Platform" }],
  viewport: "width=device-width, initial-scale=1, maximum-scale=1",
  themeColor: "#00A651",
  manifest: "/manifest.json",
  icons: {
    icon: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="antialiased min-h-screen bg-gray-50">
        {children}
      </body>
    </html>
  );
}
