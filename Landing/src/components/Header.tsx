"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "motion/react";

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-white/90 backdrop-blur-md border-b border-black/8 py-3 shadow-md"
          : "bg-[#F8F7F4]/80 backdrop-blur-sm py-4 border-b border-black/5"
      }`}
    >
      <div className="max-w-[1280px] mx-auto px-4 sm:px-6 md:px-8 flex items-center justify-between">
        {/* Brand Logo & System Status */}
        <Link href="/" className="flex items-center gap-3 group">
          <motion.div
            whileHover={{ scale: 1.05, rotate: 2 }}
            whileTap={{ scale: 0.95 }}
            className="w-8 h-8 rounded-lg bg-[#FF4500] flex items-center justify-center font-mono font-bold text-white text-xs shadow-md shadow-[#FF4500]/20"
          >
            APX
          </motion.div>
          <div className="flex flex-col">
            <span className="font-display text-base font-extrabold text-[#0C0C0E] tracking-tight flex items-center gap-2">
              APEX <span className="text-[#FF4500] text-[10px] font-mono font-semibold">v2.4</span>
            </span>
            <div className="flex items-center gap-1.5 text-[10px] font-mono text-[#059669]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#059669] animate-pulse"></span>
              <span className="font-semibold">24-LAYER OS ONLINE</span>
            </div>
          </div>
        </Link>

        {/* Desktop Nav Anchors */}
        <nav className="hidden md:flex items-center gap-7 font-mono text-[11px] text-[#52525B] font-medium tracking-wider uppercase">
          <a href="#stack" className="hover:text-[#FF4500] transition-colors">
            01. STACK
          </a>
          <a href="#dag-visualizer" className="hover:text-[#FF4500] transition-colors">
            02. ORCHESTRATOR
          </a>
          <a href="#telemetry" className="hover:text-[#FF4500] transition-colors">
            03. TELEMETRY
          </a>
          <a href="#terminal" className="hover:text-[#FF4500] transition-colors">
            04. CLI SANDBOX
          </a>
        </nav>

        {/* Action Controls */}
        <div className="hidden md:flex items-center gap-4">
          <a
            href="https://github.com/Qambar-dev-0207/realjarvis"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[11px] font-mono text-[#52525B] hover:text-[#0C0C0E] font-medium transition-colors"
          >
            [ GITHUB ]
          </a>
          <motion.a
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            href="#dag-visualizer"
            className="px-4 py-2 rounded-xl bg-[#FF4500] text-white font-mono font-bold text-[11px] tracking-wider uppercase shadow-md shadow-[#FF4500]/20 hover:bg-[#E03E00] transition-all"
          >
            LAUNCH HUD
          </motion.a>
        </div>

        {/* Mobile Toggle */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden text-[#0C0C0E] focus:outline-none"
          aria-label="Toggle Navigation Menu"
        >
          <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24">
            {mobileMenuOpen ? (
              <path fillRule="evenodd" clipRule="evenodd" d="M18.278 16.864a1 1 0 01-1.414 1.414l-4.829-4.828-4.828 4.828a1 1 0 01-1.414-1.414l4.828-4.829-4.828-4.828a1 1 0 011.414-1.414l4.829 4.828 4.828-4.828a1 1 0 111.414 1.414l-4.828 4.829 4.828 4.828z"/>
            ) : (
              <path fillRule="evenodd" clipRule="evenodd" d="M4 5h16a1 1 0 010 2H4a1 1 0 110-2zm0 6h16a1 1 0 010 2H4a1 1 0 010-2zm0 6h16a1 1 0 010 2H4a1 1 0 010-2z"/>
            )}
          </svg>
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-black/10 px-6 py-6 font-mono text-xs space-y-4 shadow-lg">
          <a href="#stack" onClick={() => setMobileMenuOpen(false)} className="block text-[#0C0C0E] font-medium">01. STACK</a>
          <a href="#dag-visualizer" onClick={() => setMobileMenuOpen(false)} className="block text-[#0C0C0E] font-medium">02. ORCHESTRATOR</a>
          <a href="#telemetry" onClick={() => setMobileMenuOpen(false)} className="block text-[#0C0C0E] font-medium">03. TELEMETRY</a>
          <a href="#terminal" onClick={() => setMobileMenuOpen(false)} className="block text-[#0C0C0E] font-medium">04. CLI SANDBOX</a>
        </div>
      )}
    </motion.header>
  );
}
