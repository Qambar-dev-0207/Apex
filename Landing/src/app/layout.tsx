import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["300", "400", "500", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "APEX — Sovereign Agentic AI OS",
  description:
    "An operating system for autonomous intelligence. From intent to coordinated execution, APEX connects planning, memory, and action in one intelligent system.",
  keywords: [
    "APEX",
    "Agentic AI OS",
    "Sovereign Intelligence",
    "Autonomous Operating System",
    "24-Layer Orchestration",
    "Task DAGs",
    "Hybrid Memory",
  ],
  authors: [{ name: "APEX Core" }],
  openGraph: {
    title: "APEX — Sovereign Agentic AI OS",
    description:
      "An operating system for autonomous intelligence. 24-Layer Orchestration, Task DAGs, Hybrid Memory.",
    type: "website",
    url: "https://github.com/Qambar-dev-0207/Apex",
  },
  twitter: {
    card: "summary_large_image",
    title: "APEX — Sovereign Agentic AI OS",
    description: "An operating system for autonomous intelligence.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable} dark scroll-smooth`}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital,wght@0,400;1,400&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-[#08090A] text-[#F3F4F2] antialiased selection:bg-[#FF3700] selection:text-[#050607] min-h-screen overflow-x-hidden font-sans">
        {children}
      </body>
    </html>
  );
}
