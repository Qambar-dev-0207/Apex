"use client";

import { ArrowUpRight } from "lucide-react";

export default function Footer() {
  const scrollTo = (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <footer
      className="w-full bg-[#050607] border-t border-[rgba(255,255,255,0.08)] py-6 sm:py-7 px-6 sm:px-10 lg:px-16 text-[#B2B0AD] select-none"
      aria-label="APEX Footer"
    >
      <div className="max-w-[1600px] mx-auto flex flex-col md:flex-row items-center justify-between gap-5 sm:gap-6">
        {/* Left: <APEX> Wordmark with Warm Orange Brackets + SOVEREIGN AGENTIC AI OS */}
        <div className="flex flex-wrap items-center gap-3 sm:gap-4">
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              window.scrollTo({ top: 0, behavior: "smooth" });
            }}
            className="flex items-center group cursor-pointer"
            aria-label="APEX - Return to top"
          >
            <span className="font-code font-bold text-base sm:text-lg text-[#FF4A16] transition-transform duration-200 group-hover:-translate-x-0.5">
              &lt;
            </span>
            <span className="font-sans font-bold text-sm sm:text-base tracking-[0.22em] text-[#F5F3EF] uppercase mx-1">
              APEX
            </span>
            <span className="font-code font-bold text-base sm:text-lg text-[#FF4A16] transition-transform duration-200 group-hover:translate-x-0.5">
              &gt;
            </span>
          </a>

          <span className="font-code text-[10px] sm:text-[11px] tracking-[0.26em] text-[#8C9295] uppercase font-normal">
            SOVEREIGN AGENTIC AI OS
          </span>
        </div>

        {/* Right: Architecture | Orchestration | Memory | Research | GitHub ↗ */}
        <nav aria-label="Footer Navigation">
          <ul className="flex flex-wrap items-center gap-6 sm:gap-8 lg:gap-10 font-sans text-xs sm:text-[13px] tracking-wider text-[#A5AAAD]">
            <li>
              <a
                href="#architecture"
                onClick={(e) => scrollTo("architecture", e)}
                className="link-underline hover:text-[#F5F3EF] transition-colors duration-200 py-1"
              >
                Architecture
              </a>
            </li>
            <li>
              <a
                href="#orchestration"
                onClick={(e) => scrollTo("orchestration", e)}
                className="link-underline hover:text-[#F5F3EF] transition-colors duration-200 py-1"
              >
                Orchestration
              </a>
            </li>
            <li>
              <a
                href="#memory"
                onClick={(e) => scrollTo("memory", e)}
                className="link-underline hover:text-[#F5F3EF] transition-colors duration-200 py-1"
              >
                Memory
              </a>
            </li>
            <li>
              <a
                href="#research"
                onClick={(e) => scrollTo("research", e)}
                className="link-underline hover:text-[#F5F3EF] transition-colors duration-200 py-1"
              >
                Research
              </a>
            </li>
            <li>
              <a
                href="https://github.com/Qambar-dev-0207/Apex"
                target="_blank"
                rel="noopener noreferrer"
                className="group link-underline inline-flex items-center gap-1.5 text-[#F5F3EF] hover:text-[#FF4A16] transition-colors duration-200 py-1 font-medium"
              >
                <span>GitHub</span>
                <ArrowUpRight
                  size={13}
                  className="transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                  aria-hidden="true"
                />
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </footer>
  );
}
