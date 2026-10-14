import type { Metadata } from "next";
import Navbar from "../../components/Navbar";
import OrchestrationSection from "../../components/OrchestrationSection";
import Footer from "../../components/Footer";

export const metadata: Metadata = {
  title: "Orchestration Engine | APEX — Sovereign Agentic AI OS",
  description:
    "Complexity, brought into order. A goal becomes a sequence of dependent tasks, coordinated toward a shared result with deterministic DAG dispatch.",
  openGraph: {
    title: "Orchestration Engine | APEX — Sovereign Agentic AI OS",
    description:
      "A goal becomes a sequence of dependent tasks, coordinated toward a shared result.",
    images: ["/apex-orchestration-bg.jpg"],
  },
};

export default function OrchestrationPage() {
  return (
    <div className="min-h-screen bg-[#050607] text-[#F5F3EF] font-sans selection:bg-[#FF4A16] selection:text-[#050607] flex flex-col justify-between">
      {/* Persistent Navigation */}
      <Navbar />

      {/* Main Orchestration Showcase */}
      <main className="w-full flex-1 flex flex-col justify-center pt-20">
        <OrchestrationSection />
      </main>

      {/* Architectural Footer */}
      <Footer />
    </div>
  );
}
