import type { Metadata } from "next";
import Navbar from "../../components/Navbar";
import ManifestoSection from "../../components/ManifestoSection";
import Footer from "../../components/Footer";

export const metadata: Metadata = {
  title: "A Different Kind of System | APEX — Sovereign Agentic AI OS",
  description:
    "A prompt is only the beginning. The real work begins after understanding the intent — planning the steps, coordinating execution, validating results, and carrying useful context forward.",
  openGraph: {
    title: "A Different Kind of System | APEX — Sovereign Agentic AI OS",
    description:
      "A prompt is only the beginning. The real work begins after understanding the intent.",
    images: ["/apex-manifesto-bg.jpg"],
  },
};

export default function ManifestoPage() {
  return (
    <div className="min-h-screen bg-[#050607] text-[#F5F3EF] font-sans selection:bg-[#FF4A16] selection:text-[#050607] flex flex-col justify-between">
      {/* Persistent Navigation */}
      <Navbar />

      {/* Main Showcase */}
      <main className="w-full flex-1 flex flex-col justify-center pt-20">
        <ManifestoSection />
      </main>

      {/* Architectural Footer */}
      <Footer />
    </div>
  );
}
