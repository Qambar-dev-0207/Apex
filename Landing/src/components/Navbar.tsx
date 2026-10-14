"use client";

import { useState, useEffect } from "react";
import { ArrowUpRight, X } from "lucide-react";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 30);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && mobileOpen) {
        setMobileOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [mobileOpen]);

  const scrollToArchitecture = (e: React.MouseEvent) => {
    e.preventDefault();
    setMobileOpen(false);
    const target = document.getElementById("architecture");
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled
          ? "bg-[#08090A]/85 backdrop-blur-md border-b border-[rgba(235,240,238,0.08)] py-4"
          : "bg-transparent py-7"
      }`}
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16 flex items-center justify-between">
        {/* Left: APEX Chevron Glyph + Wordmark + Descriptor */}
        <a
          href="#"
          className="flex items-center gap-3.5 group text-[#F3F4F2] focus-visible:outline-[#FF3700] rounded-sm"
          aria-label="APEX - Return to top"
        >
          {/* Sovereign APEX Chevron / Lambda Glyph */}
          <div className="relative w-6 h-6 flex items-center justify-center shrink-0">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="w-5 h-5 text-[#F3F4F2] transition-transform duration-300 group-hover:scale-105"
              aria-hidden="true"
            >
              <path
                d="M4 21L12 4L20 21"
                stroke="currentColor"
                strokeWidth="1.75"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M7.5 14.5L16.5 14.5"
                stroke="currentColor"
                strokeWidth="1.75"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>

          <span className="font-sans font-bold tracking-[0.26em] text-sm text-[#F3F4F2] uppercase">
            APEX
          </span>

          <span className="hidden md:inline-block w-px h-3.5 bg-[rgba(235,240,238,0.25)] mx-1.5" />

          <span className="hidden md:inline-block font-code text-[11px] tracking-[0.28em] text-[#9A9FA1] uppercase font-normal">
            SOVEREIGN INTELLIGENCE
          </span>
        </a>

        {/* Right: Architecture + View source + 2-line Hamburger Menu */}
        <div className="flex items-center gap-8 lg:gap-10">
          <nav className="hidden sm:flex items-center gap-8 font-sans text-xs tracking-wider" aria-label="Main Navigation">
            <a
              href="#architecture"
              onClick={scrollToArchitecture}
              className="text-[#9A9FA1] hover:text-[#F3F4F2] transition-colors duration-200 py-1"
            >
              Architecture
            </a>

            <a
              href="https://github.com/Qambar-dev-0207/Apex"
              target="_blank"
              rel="noopener noreferrer"
              className="group inline-flex items-center gap-1.5 text-[#F3F4F2] hover:text-white transition-colors duration-200 py-1 font-medium"
            >
              <span>View source</span>
              <ArrowUpRight
                size={13}
                className="transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                aria-hidden="true"
              />
            </a>
          </nav>

          {/* Minimal 2-Line Menu Icon */}
          <button
            type="button"
            onClick={() => setMobileOpen(!mobileOpen)}
            className="flex flex-col justify-center gap-1.5 w-6 h-6 text-[#F3F4F2] hover:opacity-80 transition-opacity focus-visible:outline-[#FF3700] p-0.5"
            aria-expanded={mobileOpen}
            aria-controls="mobile-navigation"
            aria-label={mobileOpen ? "Close navigation menu" : "Open navigation menu"}
          >
            {mobileOpen ? (
              <X size={20} />
            ) : (
              <>
                <span className="w-full h-[1.5px] bg-[#F3F4F2] block rounded-full" />
                <span className="w-full h-[1.5px] bg-[#F3F4F2] block rounded-full" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Accessible Mobile / Drawer Dropdown Menu */}
      {mobileOpen && (
        <div
          id="mobile-navigation"
          className="px-6 py-6 bg-[#08090A]/95 backdrop-blur-xl border-b border-[rgba(255,255,255,0.1)] animate-in fade-in slide-in-from-top-2 duration-200"
        >
          <div className="max-w-[1600px] mx-auto flex flex-col gap-4 font-sans text-sm">
            <span className="font-mono text-[10px] tracking-[0.25em] text-[#737575] uppercase pb-2 border-b border-[rgba(255,255,255,0.08)]">
              SYSTEM SECTIONS
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-1">
              <a
                href="#architecture"
                onClick={() => setMobileOpen(false)}
                className="text-[#B2B0AD] hover:text-[#F5F3EF] transition-colors py-1"
              >
                01 Architecture
              </a>
              <a
                href="#orchestration"
                onClick={() => setMobileOpen(false)}
                className="text-[#B2B0AD] hover:text-[#F5F3EF] transition-colors py-1"
              >
                02 Orchestration
              </a>
              <a
                href="#models"
                onClick={() => setMobileOpen(false)}
                className="text-[#B2B0AD] hover:text-[#F5F3EF] transition-colors py-1"
              >
                03 Multi-Model
              </a>
              <a
                href="#memory"
                onClick={() => setMobileOpen(false)}
                className="text-[#B2B0AD] hover:text-[#F5F3EF] transition-colors py-1"
              >
                04 Hybrid Memory
              </a>
              <a
                href="#evolution"
                onClick={() => setMobileOpen(false)}
                className="text-[#B2B0AD] hover:text-[#F5F3EF] transition-colors py-1"
              >
                05 Continuous Loop
              </a>
              <a
                href="#research"
                onClick={() => setMobileOpen(false)}
                className="text-[#B2B0AD] hover:text-[#F5F3EF] transition-colors py-1"
              >
                06 KnowledgeForge
              </a>
            </div>
            <div className="pt-3 border-t border-[rgba(255,255,255,0.08)] flex justify-between items-center">
              <a
                href="https://github.com/Qambar-dev-0207/Apex"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-[#F5F3EF] hover:text-[#FF4A16] transition-colors font-medium text-xs tracking-wider uppercase"
              >
                <span>View source on GitHub</span>
                <ArrowUpRight size={14} />
              </a>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
