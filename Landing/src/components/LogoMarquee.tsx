"use client";

const LOGOS = [
  { name: "ANTHROPIC CLAUDE 3.7", abbr: "CL" },
  { name: "GEMINI 3.8 FLASH", abbr: "GF" },
  { name: "GEMINI 3.1 PRO", abbr: "GP" },
  { name: "NVIDIA NIM HARNESS", abbr: "NV" },
  { name: "CHROMADB VECTOR", abbr: "CD" },
  { name: "REDIS WORKING CACHE", abbr: "RD" },
  { name: "MISTRAL REASONING", abbr: "MS" },
  { name: "PYTORCH KERNEL", abbr: "PT" },
  { name: "DOCKER SANDBOX", abbr: "DK" },
  { name: "FASTAPI BACKEND", abbr: "FA" },
  { name: "NEXT.JS TURBOPACK", abbr: "NX" },
];

const ALL = [...LOGOS, ...LOGOS];

export default function LogoMarquee() {
  return (
    <div className="w-full bg-white py-8 overflow-hidden relative border-y border-[#D9D9D9]">
      {/* Edge fades */}
      <div
        className="absolute left-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
        style={{ background: "linear-gradient(to right, #FFFFFF, transparent)" }}
      />
      <div
        className="absolute right-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
        style={{ background: "linear-gradient(to left, #FFFFFF, transparent)" }}
      />

      <div className="animate-marquee-left flex items-center gap-0 whitespace-nowrap">
        {ALL.map((logo, idx) => (
          <div
            key={idx}
            className="flex items-center gap-3 mx-8 opacity-60 hover:opacity-100 transition-opacity duration-200 cursor-default"
          >
            {/* Minimal icon */}
            <div className="w-6 h-6 rounded-md bg-[#F0F0F0] border border-[#D9D9D9] flex items-center justify-center">
              <span className="text-[10px] font-mono font-bold text-[#000000]">{logo.abbr}</span>
            </div>
            <span className="font-mono text-xs font-semibold text-[#000000] uppercase tracking-wider">
              {logo.name}
            </span>
            <span className="text-[#D9D9D9] text-xs mx-3">·</span>
          </div>
        ))}
      </div>
    </div>
  );
}
