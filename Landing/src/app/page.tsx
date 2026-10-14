"use client";

import Navbar from "../components/Navbar";
import HeroSection from "../components/HeroSection";
import ManifestoSection from "../components/ManifestoSection";
import ArchitectureSection from "../components/ArchitectureSection";
import OrchestrationSection from "../components/OrchestrationSection";
import ModelRoutingSection from "../components/ModelRoutingSection";
import MemorySection from "../components/MemorySection";
import EvolutionSection from "../components/EvolutionSection";
import ResearchSection from "../components/ResearchSection";
import UseCasesSection from "../components/UseCasesSection";
import FinalCTA from "../components/FinalCTA";
import Footer from "../components/Footer";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#050607] text-[#F5F3EF] font-sans selection:bg-[#FF4A16] selection:text-[#050607] relative overflow-x-hidden">
      {/* Skip to Main Content Accessibility Landmark */}
      <a
        href="#hero"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 z-[100] px-4 py-2 bg-[#F5F3EF] text-[#050607] text-xs font-semibold rounded-full shadow-lg"
      >
        Skip to main content
      </a>

      {/* Persistent Navigation */}
      <Navbar />

      {/* Complete Art-Directed Narrative Flow */}
      <main id="main-content" className="w-full">
        {/* Section 01 — Hero / The Threshold */}
        <HeroSection />

        {/* Section 02 — Manifesto / Beyond The Prompt */}
        <ManifestoSection />

        {/* Section 03 — Architecture / 24 Layers */}
        <ArchitectureSection />

        {/* Section 04 — Orchestration / From Intent to Execution */}
        <OrchestrationSection />

        {/* Section 05 — Multi-Model Intelligence */}
        <ModelRoutingSection />

        {/* Section 06 — Hybrid Memory */}
        <MemorySection />

        {/* Section 07 — Recovery and Continuous Improvement */}
        <EvolutionSection />

        {/* Section 08 — KnowledgeForge / Research into Capability */}
        <ResearchSection />

        {/* Section 09 — What APEX is Built For */}
        <UseCasesSection />

        {/* Section 10 — Final CTA / Return to the Threshold */}
        <FinalCTA />
      </main>

      {/* Section 11 — Architectural Footer */}
      <Footer />
    </div>
  );
}
