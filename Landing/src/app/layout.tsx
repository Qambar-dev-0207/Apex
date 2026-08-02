import type { Metadata } from "next";
import { Inter, Space_Grotesk, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "APEX — Sovereign Agentic AI OS",
  description:
    "A 24-Layer Sovereign Agentic AI Operating System for cognitive supremacy. Socratic reasoning gates, hybrid memory recall under 38ms, 18.4× token compression, and parallel multi-agent swarms.",
  keywords: ["Agentic AI", "Sovereign OS", "Socratic Gate", "Multi-Agent", "LLM"],
  openGraph: {
    title: "APEX — Sovereign Agentic AI OS",
    description: "Intelligence that doesn't hallucinate. A 24-Layer Agentic AI OS.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable}`}>
      <body className="bg-[#F5F4F0] text-[#0A0A0B] antialiased selection:bg-[#FF4500] selection:text-white">
        {children}
      </body>
    </html>
  );
}
