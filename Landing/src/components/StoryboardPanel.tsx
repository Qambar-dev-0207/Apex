"use client";

import { motion } from "motion/react";
import React from "react";

interface StoryboardPanelProps {
  sceneNumber: string;
  sceneTitle: string;
  shotMetadata: string;
  directorNote: string;
  children: React.ReactNode;
  id?: string;
  isActive?: boolean;
}

export default function StoryboardPanel({
  sceneNumber,
  sceneTitle,
  shotMetadata,
  directorNote,
  children,
  id,
  isActive = true,
}: StoryboardPanelProps) {
  return (
    <motion.div
      id={id}
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
      className={`editorial-card p-6 sm:p-8 relative overflow-hidden transition-all duration-300 ${
        isActive ? "border-black/15 shadow-xl" : "opacity-80"
      }`}
    >
      {/* Frame Wireframe Corner Notches */}
      <div className="absolute top-2 left-2 w-3 h-3 border-t-2 border-l-2 border-[#FF4500]/60 pointer-events-none"></div>
      <div className="absolute top-2 right-2 w-3 h-3 border-t-2 border-r-2 border-[#FF4500]/60 pointer-events-none"></div>
      <div className="absolute bottom-2 left-2 w-3 h-3 border-b-2 border-l-2 border-[#FF4500]/60 pointer-events-none"></div>
      <div className="absolute bottom-2 right-2 w-3 h-3 border-b-2 border-r-2 border-[#FF4500]/60 pointer-events-none"></div>

      {/* Storyboard Panel Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 mb-6 border-b border-black/8 font-mono text-xs">
        <div className="flex items-center gap-3">
          <span className="px-2.5 py-1 rounded bg-[#FF4500] text-white font-bold text-[11px] shadow-sm">
            {sceneNumber}
          </span>
          <span className="font-display font-extrabold text-[#0C0C0E] text-base tracking-tight">
            {sceneTitle}
          </span>
        </div>

        <div className="flex items-center gap-3 text-[#71717A] text-[11px]">
          <span className="bg-[#F8F7F4] px-2.5 py-1 rounded border border-black/5 font-semibold text-[#FF4500]">
            {shotMetadata}
          </span>
          <span className="hidden sm:inline-block font-mono text-[10px] text-[#A1A1AA]">
            16:9 STORYBOARD FRAME
          </span>
        </div>
      </div>

      {/* Storyboard Panel Interactive Content Viewport */}
      <div className="relative z-10 my-2">{children}</div>

      {/* Storyboard Director Scene Notes Footer */}
      <div className="mt-6 pt-4 border-t border-black/8 flex items-start gap-3 bg-[#F8F7F4] p-3 rounded-xl border border-black/5 font-mono text-xs">
        <span className="text-[#FF4500] font-bold shrink-0">DIRECTOR NOTE:</span>
        <span className="text-[#52525B] leading-relaxed font-medium">{directorNote}</span>
      </div>
    </motion.div>
  );
}
