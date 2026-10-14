"use client";

import { ArrowUpRight } from "lucide-react";

export default function Footer() {
  return (
    <footer
      className="w-full bg-[#050607] border-t border-[rgba(255,255,255,0.12)] py-12 sm:py-16 px-6 sm:px-10 lg:px-16 text-[#B2B0AD] select-none"
      aria-label="APEX Footer"
    >
      <div className="max-w-[1440px] mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-8 sm:gap-10">
        {/* Left: Brand & Descriptor */}
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center gap-2.5">
            <span className="font-sans font-bold text-base tracking-[0.2em] text-[#F5F3EF]">
              APEX
            </span>
            <span className="w-1.5 h-1.5 rounded-full bg-[#FF4A16]" aria-hidden="true" />
          </div>
          <span className="font-mono text-[10px] tracking-[0.24em] text-[#737575] uppercase">
            SOVEREIGN AGENTIC AI OS
          </span>
        </div>

        {/* Right: Functional Navigation Links */}
        <nav aria-label="Footer Navigation">
          <ul className="flex flex-wrap items-center gap-6 sm:gap-8 font-sans text-xs tracking-wider text-[#B2B0AD]">
            <li>
              <a
                href="#architecture"
                className="link-underline hover:text-[#F5F3EF] transition-colors duration-200"
              >
                Architecture
              </a>
            </li>
            <li>
              <a
                href="#orchestration"
                className="link-underline hover:text-[#F5F3EF] transition-colors duration-200"
              >
                Orchestration
              </a>
            </li>
            <li>
              <a
                href="#memory"
                className="link-underline hover:text-[#F5F3EF] transition-colors duration-200"
              >
                Memory
              </a>
            </li>
            <li>
              <a
                href="#research"
                className="link-underline hover:text-[#F5F3EF] transition-colors duration-200"
              >
                Research
              </a>
            </li>
            <li>
              <a
                href="https://github.com/Qambar-dev-0207/Apex"
                target="_blank"
                rel="noopener noreferrer"
                className="group link-underline inline-flex items-center gap-1 text-[#F5F3EF] hover:text-[#FF4A16] transition-colors duration-200"
              >
                <span>GitHub</span>
                <ArrowUpRight
                  size={12}
                  className="transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                  aria-hidden="true"
                />
              </a>
            </li>
          </ul>
        </nav>
      </div>

      {/* Bottom Copyright and Technical Metadata */}
      <div className="max-w-[1440px] mx-auto mt-10 pt-6 border-t border-[rgba(255,255,255,0.06)] flex flex-col sm:flex-row items-center justify-between gap-4 font-mono text-[11px] text-[#737575]">
        <span>
          © {new Date().getFullYear()} APEX OS · Sovereign Agentic Infrastructure
        </span>
        <span className="tracking-widest uppercase text-[10px]">
          24-LAYER ORCHESTRATION ENGINE
        </span>
      </div>
    </footer>
  );
}
