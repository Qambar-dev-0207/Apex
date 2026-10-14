"use client";

import { ArrowUp, ArrowUpRight } from "lucide-react";

export default function ClosingSection() {
  const scrollToTop = (e: React.MouseEvent) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <section
      id="closing"
      className="relative w-full bg-[#08090A] border-t border-[rgba(235,240,238,0.1)] py-36 sm:py-44 overflow-hidden select-none"
      aria-label="APEX Conclusion & Source Code"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        <div className="max-w-[760px] mx-auto text-center flex flex-col items-center">
          {/* APEX Sovereign Chevron Glyph */}
          <div className="w-8 h-8 mb-8 text-[#F3F4F2] flex items-center justify-center">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="w-7 h-7"
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

          {/* Headline */}
          <h2 className="font-editorial text-5xl sm:text-7xl lg:text-8xl tracking-[-0.02em] text-[#F3F4F2] mb-6 leading-tight">
            Go beyond the prompt.
          </h2>

          {/* Supporting Copy */}
          <p className="text-[#9A9FA1] text-base sm:text-lg font-normal mb-10 max-w-md">
            Explore the architecture behind APEX.
          </p>

          {/* Primary CTA and Understated Back to Top */}
          <div className="flex flex-wrap items-center justify-center gap-5 mb-24">
            <a
              href="https://github.com/Qambar-dev-0207/Apex"
              target="_blank"
              rel="noopener noreferrer"
              className="group inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-[#F3F4F2] text-[#08090A] font-sans text-xs tracking-wider font-semibold transition-all duration-200 hover:bg-white hover:scale-[1.02] active:scale-[0.98] focus-visible:outline-[#FF3700] shadow-md"
            >
              <span>Explore APEX on GitHub</span>
              <ArrowUpRight
                size={14}
                className="transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                aria-hidden="true"
              />
            </a>

            <button
              type="button"
              onClick={scrollToTop}
              className="group inline-flex items-center gap-1.5 px-5 py-3.5 rounded-full text-[#9A9FA1] hover:text-[#F3F4F2] font-sans text-xs tracking-wider transition-colors duration-200 border border-[rgba(235,240,238,0.13)] hover:border-[rgba(235,240,238,0.28)] focus-visible:outline-[#FF3700] cursor-pointer"
            >
              <span>Back to top</span>
              <ArrowUp
                size={14}
                className="transition-transform duration-200 group-hover:-translate-y-0.5"
                aria-hidden="true"
              />
            </button>
          </div>

          {/* Minimal Precision Metadata Footer */}
          <div className="w-full pt-8 border-t border-[rgba(235,240,238,0.08)] flex flex-col sm:flex-row items-center justify-between gap-4 text-[#676D70] font-code text-[11px] tracking-[0.24em] uppercase">
            <span>APEX · SOVEREIGN AGENTIC AI OS</span>
            <span>OPEN SOVEREIGN ARCHITECTURE · 2026</span>
          </div>
        </div>
      </div>
    </section>
  );
}
