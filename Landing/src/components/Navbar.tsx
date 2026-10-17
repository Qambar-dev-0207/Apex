"use client";

import { useState, useEffect } from "react";
import { ArrowUpRight, X } from "lucide-react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const shouldReduceMotion = useReducedMotion();

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

  const navLinks = [
    { num: "01", label: "Architecture", href: "#architecture" },
    { num: "02", label: "Orchestration", href: "#orchestration" },
    { num: "03", label: "Multi-Model", href: "#models" },
    { num: "04", label: "Hybrid Memory", href: "#memory" },
    { num: "05", label: "Continuous Loop", href: "#evolution" },
    { num: "06", label: "KnowledgeForge", href: "#research" },
  ];

  return (
    <motion.header
      initial={shouldReduceMotion ? { y: 0, opacity: 1 } : { y: -16, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 select-none ${
        scrolled
          ? "bg-[#08090A]/85 backdrop-blur-md border-b border-[rgba(255,255,255,0.08)] py-4"
          : "bg-transparent py-7"
      }`}
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16 flex items-center justify-between">
        {/* Left: APEX Chevron Glyph + Wordmark + Descriptor */}
        <a
          href="#"
          className="flex items-center gap-3.5 group text-[#F5F3EF] focus-visible:outline-[#FF4A16] rounded-sm"
          aria-label="APEX - Return to top"
        >
          {/* Sovereign APEX Chevron / Lambda Glyph */}
          <div className="relative w-6 h-6 flex items-center justify-center shrink-0">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="w-5 h-5 text-[#F5F3EF] transition-transform duration-300 group-hover:scale-105"
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

          <span className="font-sans font-bold tracking-[0.26em] text-sm text-[#F5F3EF] uppercase">
            APEX
          </span>

          <span className="hidden md:inline-block w-px h-3.5 bg-[rgba(255,255,255,0.2)] mx-1.5" />

          <span className="hidden md:inline-block font-code text-[11px] tracking-[0.28em] text-[#9A9FA1] uppercase font-normal">
            SOVEREIGN AGENTIC AI OS
          </span>
        </a>

        {/* Right: Architecture + Orchestration + Research + View source + 2-line Menu Control */}
        <div className="flex items-center gap-7 lg:gap-8">
          <nav className="hidden md:flex items-center gap-6 lg:gap-8 font-sans text-xs tracking-wider" aria-label="Main Navigation">
            <a
              href="#architecture"
              onClick={scrollToArchitecture}
              className="link-underline text-[#B2B0AD] hover:text-[#F5F3EF] transition-colors duration-200 py-1"
            >
              Architecture
            </a>

            <a
              href="#orchestration"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById("orchestration")?.scrollIntoView({ behavior: "smooth" });
              }}
              className="link-underline text-[#B2B0AD] hover:text-[#F5F3EF] transition-colors duration-200 py-1"
            >
              Orchestration
            </a>

            <a
              href="#research"
              onClick={(e) => {
                e.preventDefault();
                document.getElementById("research")?.scrollIntoView({ behavior: "smooth" });
              }}
              className="link-underline text-[#B2B0AD] hover:text-[#F5F3EF] transition-colors duration-200 py-1"
            >
              Research
            </a>

            <a
              href="https://github.com/Qambar-dev-0207/Apex"
              target="_blank"
              rel="noopener noreferrer"
              className="group link-underline inline-flex items-center gap-1.5 text-[#F5F3EF] hover:text-white transition-colors duration-200 py-1 font-medium"
            >
              <span>View source</span>
              <ArrowUpRight
                size={13}
                className="transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 text-[#9A9FA1] group-hover:text-white"
                aria-hidden="true"
              />
            </a>
          </nav>

          {/* Minimal 2-Line Menu Icon */}
          <button
            type="button"
            onClick={() => setMobileOpen(!mobileOpen)}
            className="flex flex-col justify-center gap-1.5 w-6 h-6 text-[#F5F3EF] hover:opacity-80 transition-opacity focus-visible:outline-[#FF4A16] p-0.5 cursor-pointer"
            aria-expanded={mobileOpen}
            aria-controls="mobile-navigation"
            aria-label={mobileOpen ? "Close navigation menu" : "Open navigation menu"}
          >
            {mobileOpen ? (
              <X size={20} />
            ) : (
              <>
                <span className="w-full h-[1.5px] bg-[#F5F3EF] block rounded-full" />
                <span className="w-full h-[1.5px] bg-[#F5F3EF] block rounded-full" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Accessible Mobile / Drawer Dropdown Menu with Staggered Links */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            id="mobile-navigation"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
            className="px-6 py-6 bg-[#08090A]/95 backdrop-blur-xl border-b border-[rgba(255,255,255,0.1)]"
          >
            <div className="max-w-[1600px] mx-auto flex flex-col gap-4 font-sans text-sm">
              <span className="font-mono text-[10px] tracking-[0.25em] text-[#737575] uppercase pb-2 border-b border-[rgba(255,255,255,0.08)]">
                SYSTEM SECTIONS
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-1">
                {navLinks.map((item, idx) => (
                  <motion.a
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{
                      duration: 0.3,
                      delay: 0.1 + idx * 0.06,
                      ease: [0.16, 1, 0.3, 1],
                    }}
                    className="link-underline text-[#B2B0AD] hover:text-[#F5F3EF] transition-colors py-1 inline-flex items-center gap-1.5"
                  >
                    <span className="font-code text-[11px] text-[#FF4A16]">{item.num}</span>
                    <span>{item.label}</span>
                  </motion.a>
                ))}
              </div>

              <motion.div
                initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: 0.3,
                  delay: 0.1 + navLinks.length * 0.06,
                  ease: [0.16, 1, 0.3, 1],
                }}
                className="pt-3 border-t border-[rgba(255,255,255,0.08)] flex justify-between items-center"
              >
                <a
                  href="https://github.com/Qambar-dev-0207/Apex"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group link-underline inline-flex items-center gap-1.5 text-[#F5F3EF] hover:text-[#FF4A16] transition-colors font-medium text-xs tracking-wider uppercase"
                >
                  <span>View source on GitHub</span>
                  <ArrowUpRight
                    size={14}
                    className="transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                  />
                </a>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
