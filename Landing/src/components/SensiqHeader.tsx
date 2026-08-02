"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { motion, useMotionValue, useSpring } from "motion/react";

function MagneticButton({ children, className, href }: { children: React.ReactNode; className?: string; href?: string }) {
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

export default function ApexHeader() {
  const [scrolled, setScrolled] = useState(false);
  const [activeTab, setActiveTab] = useState("Overview");
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navItems = [
    { label: "Overview", href: "#overview" },
    { label: "Architecture", href: "#stack" },
    { label: "Playground", href: "#playground" },
    { label: "Telemetry", href: "#telemetry" },
  ];

  return (
    <motion.header
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="fixed top-0 left-0 right-0 z-50 px-4 sm:px-6"
    >
      <div
        className={`max-w-[1340px] mx-auto mt-4 flex items-center justify-between px-4 py-3 rounded-2xl transition-all duration-300 ${
          scrolled
            ? "bg-white/92 backdrop-blur-2xl shadow-[0_4px_24px_rgba(0,0,0,0.08)] border border-black/8"
            : "bg-transparent"
        }`}
      >
        {/* Wordmark */}
        <Link href="/" className="group flex items-center gap-2.5">
          <div className="relative w-8 h-8 rounded-lg bg-[#0A0A0B] flex items-center justify-center shadow-sm">
            <span className="text-white font-bold text-xs font-display tracking-wide">Ax</span>
            <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-[#65CC00] shadow-[0_0_4px_#65CC00]" />
          </div>
          <span className="font-display font-bold text-[#0A0A0B] text-lg tracking-tight group-hover:opacity-75 transition-opacity">
            APEX
          </span>
        </Link>

        {/* Center Nav — desktop */}
        <nav className="hidden md:flex items-center">
          <div className={`flex items-center gap-1 px-2 py-2 rounded-xl transition-all duration-300 ${scrolled ? "" : "bg-white/60 backdrop-blur-lg border border-black/6 shadow-sm"}`}>
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                onClick={() => setActiveTab(item.label)}
                className={`relative px-4 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  activeTab === item.label
                    ? "text-[#0A0A0B] font-semibold"
                    : "text-[#6B7280] hover:text-[#0A0A0B]"
                }`}
              >
                {activeTab === item.label && (
                  <motion.span
                    layoutId="nav-active"
                    className="absolute inset-0 bg-white rounded-lg shadow-sm border border-black/6"
                    style={{ zIndex: -1 }}
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  />
                )}
                {item.label}
              </a>
            ))}
          </div>
        </nav>

        {/* Right: CTA */}
        <div className="flex items-center gap-3">
          {/* GitHub ghost link */}
          <a
            href="https://github.com/Qambar-dev-0207/realjarvis"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium text-[#6B7280] hover:text-[#0A0A0B] transition-colors"
          >
            GitHub
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>

          {/* Magnetic vermilion CTA */}
          <MagneticButton
            href="#orchestrator"
            className="magnetic-btn px-5 py-2.5 rounded-xl bg-[#FF4500] text-white text-sm font-semibold tracking-wide shadow-[0_4px_14px_rgba(255,69,0,0.35)] hover:bg-[#E03E00] hover:shadow-[0_6px_20px_rgba(255,69,0,0.45)] transition-all duration-200"
          >
            Launch HUD
          </MagneticButton>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden w-9 h-9 flex flex-col items-center justify-center gap-1.5 rounded-lg bg-white/80 border border-black/8 shadow-sm"
          >
            <span className={`w-5 h-0.5 bg-[#0A0A0B] rounded-full transition-transform ${mobileOpen ? "rotate-45 translate-y-2" : ""}`} />
            <span className={`w-5 h-0.5 bg-[#0A0A0B] rounded-full transition-opacity ${mobileOpen ? "opacity-0" : ""}`} />
            <span className={`w-5 h-0.5 bg-[#0A0A0B] rounded-full transition-transform ${mobileOpen ? "-rotate-45 -translate-y-2" : ""}`} />
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="md:hidden max-w-[1340px] mx-auto mt-2 bg-white/95 backdrop-blur-2xl border border-black/8 rounded-2xl shadow-xl p-4 space-y-1"
        >
          {navItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              onClick={() => { setActiveTab(item.label); setMobileOpen(false); }}
              className="block px-4 py-3 rounded-xl text-sm font-medium text-[#0A0A0B] hover:bg-black/4 transition-colors"
            >
              {item.label}
            </a>
          ))}
          <div className="pt-2 border-t border-black/6">
            <a
              href="#orchestrator"
              className="block px-4 py-3 rounded-xl text-sm font-semibold text-white bg-[#FF4500] text-center"
            >
              Launch HUD
            </a>
          </div>
        </motion.div>
      )}
    </motion.header>
  );
}
