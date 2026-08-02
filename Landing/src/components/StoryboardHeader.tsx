"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "motion/react";

interface StoryboardHeaderProps {
  activeScene: number;
  onSelectScene: (sceneIdx: number) => void;
  isAutoPlaying: boolean;
  onToggleAutoPlay: () => void;
  viewMode: "scroll" | "focus";
  onToggleViewMode: () => void;
}

const SCENES = [
  { id: "scene-1", label: "SCENE 01: INTENT" },
  { id: "scene-2", label: "SCENE 02: SOCRATIC" },
  { id: "scene-3", label: "SCENE 03: MEMORY" },
  { id: "scene-4", label: "SCENE 04: SWARM" },
  { id: "scene-5", label: "SCENE 05: VITALS" },
  { id: "scene-6", label: "SCENE 06: DEPLOY" },
];

export default function StoryboardHeader({
  activeScene,
  onSelectScene,
  isAutoPlaying,
  onToggleAutoPlay,
  viewMode,
  onToggleViewMode,
}: StoryboardHeaderProps) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-white/95 backdrop-blur-md border-b border-black/10 py-2.5 shadow-md"
          : "bg-[#F8F7F4]/90 backdrop-blur-sm py-3 border-b border-black/8"
      }`}
    >
      <div className="max-w-[1340px] mx-auto px-4 sm:px-6 md:px-8 flex flex-wrap items-center justify-between gap-3">
        {/* Brand & Status */}
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-[#FF4500] text-white flex items-center justify-center font-mono font-bold text-xs shadow-sm">
            APX
          </div>
          <div className="flex flex-col">
            <span className="font-display text-sm font-extrabold text-[#0C0C0E] tracking-tight flex items-center gap-1.5">
              APEX <span className="text-[#FF4500] text-[10px] font-mono font-semibold">v2.4 STORYBOARD</span>
            </span>
          </div>
        </Link>

        {/* Storyboard Scene Map Scrubber */}
        <div className="hidden lg:flex items-center gap-1 bg-[#F3F1EC] p-1 rounded-xl border border-black/8 font-mono text-[11px]">
          {SCENES.map((scene, idx) => (
            <button
              key={scene.id}
              onClick={() => onSelectScene(idx)}
              className={`px-2.5 py-1 rounded-lg transition-all ${
                activeScene === idx
                  ? "bg-[#FF4500] text-white font-bold shadow-sm"
                  : "text-[#52525B] hover:text-[#0C0C0E] hover:bg-black/5"
              }`}
            >
              {scene.label}
            </button>
          ))}
        </div>

        {/* Storyboard Controls */}
        <div className="flex items-center gap-2 font-mono text-xs">
          {/* Auto Play Stepper */}
          <button
            onClick={onToggleAutoPlay}
            className={`px-3 py-1.5 rounded-lg border font-semibold transition-all flex items-center gap-1.5 ${
              isAutoPlaying
                ? "bg-[#059669] text-white border-[#059669] shadow-sm"
                : "bg-white text-[#0C0C0E] border-black/10 hover:border-[#FF4500]"
            }`}
          >
            <span>{isAutoPlaying ? "PAUSE ▶" : "PLAY STORYBOARD ▶"}</span>
          </button>

          {/* View Mode Toggle */}
          <button
            onClick={onToggleViewMode}
            className="hidden sm:flex px-3 py-1.5 rounded-lg bg-[#0C0C0E] text-white font-semibold hover:bg-black transition-all"
          >
            {viewMode === "scroll" ? "FRAME FOCUS MODE" : "FULL SCROLL MODE"}
          </button>

          <a
            href="https://github.com/Qambar-dev-0207/realjarvis"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:block text-[11px] text-[#52525B] hover:text-[#0C0C0E] font-medium ml-1"
          >
            [ GITHUB ]
          </a>
        </div>
      </div>
    </header>
  );
}
