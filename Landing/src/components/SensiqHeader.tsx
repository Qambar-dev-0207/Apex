"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { motion, useMotionValue, useSpring, AnimatePresence } from "motion/react";

/* ─── Magnetic CTA Button ──────────────────────────────── */
function MagneticButton({
  children,
  className,
  href,
}: {
  children: React.ReactNode;
  className?: string;
  href?: string;
}) {
  const ref = useRef<HTMLAnchorElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const springX = useSpring(x, { stiffness: 300, damping: 25 });
  const springY = useSpring(y, { stiffness: 300, damping: 25 });

  const handleMouse = (e: React.MouseEvent) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    x.set((e.clientX - cx) * 0.25);
    y.set((e.clientY - cy) * 0.25);
  };

  const handleLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.a
      ref={ref}
      href={href || "#"}
      style={{ x: springX, y: springY }}
      onMouseMove={handleMouse}
      onMouseLeave={handleLeave}
      className={className}
    >
      {children}
    </motion.a>
  );
}

/* ─── Mega Menu Dropdown Component ─────────────────────── */
function DevelopersMegaMenu({ onClose }: { onClose: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 8, scale: 0.98 }}
      transition={{ duration: 0.24, ease: [0.16, 1, 0.3, 1] }}
      className="absolute top-full left-1/2 -translate-x-1/2 mt-3 w-[720px] max-w-[calc(100vw-32px)] bg-white rounded-3xl border border-[#D9D9D9] shadow-[0_24px_64px_-12px_rgba(10,10,11,0.12)] overflow-hidden z-50"
    >
      {/* ─── Top 2-Column Grid ─── */}
      <div className="grid grid-cols-1 md:grid-cols-2">
        {/* Left Column: Guides */}
        <Link
          href="#process"
          onClick={onClose}
          className="group p-7 flex flex-col justify-between border-b md:border-b-0 md:border-r border-[#D9D9D9] hover:bg-[#FAFAF9] transition-colors relative"
        >
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <h3 className="font-display font-bold text-base text-[#0A0A0B] group-hover:text-[#FF4500] transition-colors">
                Guides
              </h3>
              <span className="font-mono text-[10px] font-semibold text-[#65CC00] bg-[#65CC00]/10 px-2 py-0.5 rounded-full">
                Socratic OS
              </span>
            </div>
            <p className="text-[#6B7280] text-[13px] leading-relaxed max-w-[280px]">
              Learn, orchestrate, verify: Step-by-step Socratic invariant protocols &amp; multi-agent swarm guides.
            </p>
          </div>

          {/* Schematic Blueprint Illustration (Organic Contour Blueprint) */}
          <div className="mt-6 w-full h-[180px] flex items-center justify-center relative overflow-hidden pointer-events-none">
            <svg viewBox="0 0 240 200" className="w-full h-full opacity-80">
              {/* Construction guide axis */}
              <line x1="10" y1="190" x2="230" y2="10" stroke="#E5E7EB" strokeWidth="1" strokeDasharray="3 3" />
              <line x1="20" y1="100" x2="220" y2="100" stroke="#F0F0F0" strokeWidth="1" strokeDasharray="2 2" />

              {/* Concentric outer circular guide */}
              <circle cx="120" cy="110" r="76" fill="none" stroke="#E5E7EB" strokeWidth="1" />
              <circle cx="120" cy="110" r="76" fill="none" stroke="#D1D5DB" strokeWidth="1" strokeDasharray="4 4" />

              {/* Organic contour loops (metaball blueprint) */}
              <path
                d="M 85,90 C 85,75 105,65 125,75 C 145,85 160,80 165,95 C 170,110 155,125 155,140 C 155,155 135,160 120,150 C 105,140 85,150 75,135 C 65,120 85,105 85,90 Z"
                fill="none"
                stroke="#D1D5DB"
                strokeWidth="1.5"
                strokeDasharray="3 3"
              />
              <path
                d="M 92,95 C 92,82 108,74 122,82 C 138,90 150,86 154,98 C 158,110 146,122 146,134 C 146,146 130,150 118,142 C 106,134 90,142 82,130 C 74,118 92,108 92,95 Z"
                fill="none"
                stroke="#9CA3AF"
                strokeWidth="1.5"
                className="group-hover:stroke-[#FF4500] transition-colors duration-300"
              />

              {/* Internal dotted network nodes */}
              <circle cx="120" cy="110" r="4" fill="#0A0A0B" />
              <circle cx="145" cy="85" r="3" fill="#D1D5DB" />
              <circle cx="95" cy="130" r="3" fill="#D1D5DB" />
              <circle cx="150" cy="135" r="2.5" fill="#D1D5DB" />
              <circle cx="75" cy="95" r="2.5" fill="#D1D5DB" />
            </svg>
          </div>
        </Link>

        {/* Right Column: Split into Tools & Case studies */}
        <div className="flex flex-col">
          {/* Top Right: Tools */}
          <Link
            href="#telemetry"
            onClick={onClose}
            className="group p-6 border-b border-[#D9D9D9] hover:bg-[#FAFAF9] transition-colors flex-1 flex flex-col justify-between"
          >
            <div>
              <h3 className="font-display font-bold text-base text-[#0A0A0B] mb-1 group-hover:text-[#FF4500] transition-colors">
                Tools
              </h3>
              <p className="text-[#6B7280] text-[13px] leading-relaxed max-w-[280px]">
                Our resources include the AST symbol pruner, vector cache inspector, and hardware vitals.
              </p>
            </div>

            {/* Binary / AST Bit Stream Diagram */}
            <div className="mt-4 pt-3 flex items-center justify-center font-mono text-[13px] tracking-widest text-[#9CA3AF] pointer-events-none select-none">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[#9CA3AF]">0110010100</span>
                  <span className="w-px h-3.5 bg-[#D1D5DB]" />
                  <span className="text-[#0A0A0B] font-semibold group-hover:text-[#FF4500] transition-colors">101</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[#9CA3AF]">1010101010</span>
                  <span className="w-px h-3.5 bg-[#D1D5DB]" />
                  <span className="text-[#0A0A0B] font-semibold group-hover:text-[#FF4500] transition-colors">111</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[#9CA3AF]">1010001110</span>
                  <span className="w-px h-3.5 bg-[#D1D5DB]" />
                  <span className="text-[#0A0A0B] font-semibold group-hover:text-[#FF4500] transition-colors">100</span>
                </div>
              </div>
            </div>
          </Link>

          {/* Bottom Right: Case studies */}
          <Link
            href="#work"
            onClick={onClose}
            className="group p-6 hover:bg-[#FAFAF9] transition-colors flex-1 flex flex-col justify-between"
          >
            <div>
              <h3 className="font-display font-bold text-base text-[#0A0A0B] mb-1 group-hover:text-[#FF4500] transition-colors">
                Case studies
              </h3>
              <p className="text-[#6B7280] text-[13px] leading-relaxed max-w-[280px]">
                Our customers stories are the only ones that matter: verified 0% hallucination workloads.
              </p>
            </div>

            {/* Technical Distribution / Latency Bell Curve Diagram */}
            <div className="mt-4 pt-2 w-full h-[65px] relative pointer-events-none flex items-center justify-center">
              <svg viewBox="0 0 220 60" className="w-full h-full">
                {/* Outer frame */}
                <rect x="5" y="5" width="210" height="50" fill="none" stroke="#E5E7EB" strokeWidth="1" />
                {/* Vertical grid lines */}
                <line x1="45" y1="5" x2="45" y2="55" stroke="#E5E7EB" strokeWidth="1" strokeDasharray="3 3" />
                <line x1="85" y1="5" x2="85" y2="55" stroke="#CBD5E1" strokeWidth="1.5" />
                <line x1="125" y1="5" x2="125" y2="55" stroke="#E5E7EB" strokeWidth="1" strokeDasharray="3 3" />
                <line x1="165" y1="5" x2="165" y2="55" stroke="#E5E7EB" strokeWidth="1" strokeDasharray="3 3" />

                {/* Primary Bell Curve */}
                <path
                  d="M 10,50 Q 85,10 110,12 T 210,50"
                  fill="none"
                  stroke="#9CA3AF"
                  strokeWidth="1.5"
                  className="group-hover:stroke-[#FF4500] transition-colors duration-300"
                />
                {/* Secondary Lower Curve */}
                <path
                  d="M 10,52 Q 85,25 110,26 T 210,52"
                  fill="none"
                  stroke="#D1D5DB"
                  strokeWidth="1"
                />
              </svg>
            </div>
          </Link>
        </div>
      </div>

      {/* ─── Bottom Banner: API Documentation ─── */}
      <div className="p-5 px-7 bg-[#FAFAF9] border-t border-[#D9D9D9] flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-2xl bg-white border border-[#D9D9D9] shadow-xs flex items-center justify-center text-[#0A0A0B] shrink-0">
            {/* Book / Terminal icon */}
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <div>
            <h4 className="font-display font-bold text-sm text-[#0A0A0B]">
              API Documentation
            </h4>
            <p className="text-[#6B7280] text-xs">
              Everything you need to interact with APEX Sovereign Kernel via API.
            </p>
          </div>
        </div>

        <Link
          href="#playground"
          onClick={onClose}
          className="shrink-0 px-4 py-2 rounded-xl bg-white border border-[#D9D9D9] hover:border-[#0A0A0B] text-xs font-semibold text-[#0A0A0B] shadow-xs hover:shadow-sm transition-all inline-flex items-center gap-1.5"
        >
          <span>Read docs</span>
          <span className="text-[#6B7280]">›</span>
        </Link>
      </div>
    </motion.div>
  );
}

/* ─── Main Navbar Header ───────────────────────────────── */
export default function ApexHeader() {
  const [scrolled, setScrolled] = useState(false);
  const [developersOpen, setDevelopersOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 30);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleMouseEnter = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setDevelopersOpen(true);
  };

  const handleMouseLeave = () => {
    timeoutRef.current = setTimeout(() => {
      setDevelopersOpen(false);
    }, 180);
  };

  return (
    <motion.header
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="fixed top-0 left-0 right-0 z-50 px-4 sm:px-8 pt-4"
    >
      <div className="max-w-[1340px] mx-auto relative">
        {/* Floating Navbar Pill */}
        <div
          className={`flex items-center justify-between px-5 py-3 rounded-2xl transition-all duration-300 ${
            scrolled
              ? "bg-white/95 backdrop-blur-2xl shadow-[0_10px_30px_rgba(0,0,0,0.06)] border border-[#D9D9D9]"
              : "bg-white border border-[#D9D9D9] shadow-sm"
          }`}
        >
          {/* Left Cluster: Logo & Navigation */}
          <div className="flex items-center gap-7">
            {/* Brand Logo Wordmark */}
            <Link href="/" className="group flex items-center gap-2.5">
              <div className="relative w-8 h-8 rounded-xl bg-[#0A0A0B] flex items-center justify-center shadow-xs">
                <span className="text-white font-bold text-xs font-display tracking-wide">Ax</span>
                <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-[#65CC00] shadow-[0_0_4px_#65CC00]" />
              </div>
              <span className="font-display font-bold text-[#0A0A0B] text-lg tracking-tight group-hover:opacity-80 transition-opacity">
                APEX
              </span>
            </Link>

            {/* Desktop Nav Items */}
            <nav className="hidden md:flex items-center gap-1 font-medium text-sm text-[#0A0A0B]">
              {/* Developers with Mega-Menu Dropdown */}
              <div
                className="relative py-1"
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
              >
                <button
                  onClick={() => setDevelopersOpen(!developersOpen)}
                  className={`px-3.5 py-1.5 rounded-xl inline-flex items-center gap-1.5 transition-colors cursor-pointer ${
                    developersOpen ? "text-[#FF4500] font-semibold bg-black/4" : "text-[#0A0A0B] hover:text-[#FF4500]"
                  }`}
                >
                  <span>Developers</span>
                  <svg
                    className={`w-3.5 h-3.5 transition-transform duration-200 ${
                      developersOpen ? "rotate-180 text-[#FF4500]" : "text-[#9CA3AF]"
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>

              {/* Pricing */}
              <Link
                href="#pricing"
                className="px-3.5 py-1.5 rounded-xl hover:text-[#FF4500] transition-colors"
              >
                Pricing
              </Link>

              {/* Architecture */}
              <Link
                href="#stack"
                className="px-3.5 py-1.5 rounded-xl hover:text-[#FF4500] transition-colors"
              >
                Architecture
              </Link>

              {/* About */}
              <Link
                href="#process"
                className="px-3.5 py-1.5 rounded-xl hover:text-[#FF4500] transition-colors"
              >
                About
              </Link>
            </nav>
          </div>

          {/* Right Cluster: Actions */}
          <div className="flex items-center gap-3">
            {/* Sign in / GitHub Link */}
            <a
              href="https://github.com/Qambar-dev-0207/realjarvis"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-sm font-medium text-[#0A0A0B] hover:text-[#FF4500] transition-colors"
            >
              Sign in
            </a>

            {/* Primary Vermilion CTA Button (Matching "Get started" from reference) */}
            <MagneticButton
              href="#orchestrator"
              className="px-5 py-2 rounded-xl bg-[#FF4500] text-white text-sm font-semibold tracking-wide shadow-[0_4px_14px_rgba(255,69,0,0.32)] hover:bg-[#E03E00] hover:shadow-[0_6px_20px_rgba(255,69,0,0.45)] transition-all duration-200 cursor-pointer"
            >
              Get started
            </MagneticButton>

            {/* Mobile Hamburger Button */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden w-9 h-9 flex flex-col items-center justify-center gap-1.5 rounded-xl bg-white border border-[#D9D9D9] shadow-xs cursor-pointer"
              aria-label="Toggle navigation"
            >
              <span className={`w-4 h-0.5 bg-[#0A0A0B] rounded-full transition-transform ${mobileOpen ? "rotate-45 translate-y-2" : ""}`} />
              <span className={`w-4 h-0.5 bg-[#0A0A0B] rounded-full transition-opacity ${mobileOpen ? "opacity-0" : ""}`} />
              <span className={`w-4 h-0.5 bg-[#0A0A0B] rounded-full transition-transform ${mobileOpen ? "-rotate-45 -translate-y-2" : ""}`} />
            </button>
          </div>
        </div>

        {/* ─── Mega Menu Dropdown Overlay ─── */}
        <div
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          <AnimatePresence>
            {developersOpen && (
              <DevelopersMegaMenu onClose={() => setDevelopersOpen(false)} />
            )}
          </AnimatePresence>
        </div>

        {/* ─── Mobile Drawer ─── */}
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="md:hidden mt-2 bg-white border border-[#D9D9D9] rounded-2xl shadow-xl p-4 space-y-2"
          >
            <Link
              href="#process"
              onClick={() => setMobileOpen(false)}
              className="block px-4 py-2.5 rounded-xl text-sm font-medium text-[#0A0A0B] hover:bg-black/4"
            >
              Guides &amp; Architecture
            </Link>
            <Link
              href="#telemetry"
              onClick={() => setMobileOpen(false)}
              className="block px-4 py-2.5 rounded-xl text-sm font-medium text-[#0A0A0B] hover:bg-black/4"
            >
              Tools &amp; Telemetry
            </Link>
            <Link
              href="#work"
              onClick={() => setMobileOpen(false)}
              className="block px-4 py-2.5 rounded-xl text-sm font-medium text-[#0A0A0B] hover:bg-black/4"
            >
              Case Studies
            </Link>
            <Link
              href="#pricing"
              onClick={() => setMobileOpen(false)}
              className="block px-4 py-2.5 rounded-xl text-sm font-medium text-[#0A0A0B] hover:bg-black/4"
            >
              Pricing
            </Link>
            <Link
              href="#playground"
              onClick={() => setMobileOpen(false)}
              className="block px-4 py-2.5 rounded-xl text-sm font-medium text-[#0A0A0B] hover:bg-black/4"
            >
              API Documentation
            </Link>
            <div className="pt-2 border-t border-[#D9D9D9]">
              <Link
                href="#orchestrator"
                onClick={() => setMobileOpen(false)}
                className="block px-4 py-2.5 rounded-xl text-sm font-semibold text-white bg-[#FF4500] text-center"
              >
                Get started
              </Link>
            </div>
          </motion.div>
        )}
      </div>
    </motion.header>
  );
}
