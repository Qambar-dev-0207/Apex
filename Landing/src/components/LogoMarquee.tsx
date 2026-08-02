"use client";

const LOGOS = [
  { name: "GEMINI 2.0 FLASH", abbr: "GF" },
  { name: "ANTHROPIC CLAUDE 3.5", abbr: "CL" },
  { name: "DOCKER ISOLATION", abbr: "DK" },
  { name: "REDIS WORKING DB", abbr: "RD" },
  { name: "CHROMADB VECTOR", abbr: "CD" },
  { name: "PYTORCH COMPUTE", abbr: "PT" },
  { name: "OPENROUTER", abbr: "OR" },
  { name: "LANGCHAIN / AST", abbr: "LC" },
  { name: "FASTAPI BACKEND", abbr: "FA" },
  { name: "NEXT.JS FRONTEND", abbr: "NX" },
];

// Duplicate for seamless loop
const ALL = [...LOGOS, ...LOGOS];

export default function LogoMarquee() {
  return (
    <div className="w-full bg-[#0A0A0B] py-10 overflow-hidden relative">
      {/* Edge fades */}
      <div className="absolute left-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
           style={{ background: "linear-gradient(to right, #0A0A0B, transparent)" }} />
      <div className="absolute right-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
           style={{ background: "linear-gradient(to left, #0A0A0B, transparent)" }} />

      <div className="animate-marquee-left flex items-center gap-0 whitespace-nowrap">
        {ALL.map((logo, idx) => (
          <div
            key={idx}
            className="flex items-center gap-3 mx-8 opacity-55 hover:opacity-100 transition-opacity duration-300 cursor-default"
          >
            {/* Minimal icon */}
            <div className="w-6 h-6 rounded-md bg-white/10 flex items-center justify-center">
              <span className="text-[9px] font-mono font-bold text-white/70">{logo.abbr}</span>
            </div>
            <span className="font-mono text-xs font-semibold text-white/70 uppercase tracking-widest">
              {logo.name}
            </span>
            <span className="text-white/15 text-xs mx-2">·</span>
          </div>
        ))}
      </div>
    </div>
  );
}
