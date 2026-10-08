"use client";

import { useEffect, useRef, useState } from "react";

interface TelemetryCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  type: "sine" | "bars" | "random";
  color?: "cyan" | "violet" | "emerald" | "amber";
}

export default function TelemetryCard({
  title,
  value,
  unit = "",
  subtext = "",
  type,
  color = "amber",
}: TelemetryCardProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [liveVal, setLiveVal] = useState<number | string>(value);

  // Hanzo Strictly Controlled Palette
  const colorMap: Record<string, { stroke: string; dot: string }> = {
    emerald: { stroke: "#0CB300", dot: "#0CB300" },
    amber: { stroke: "#FF3700", dot: "#FF3700" },
    cyan: { stroke: "#000000", dot: "#000000" },
    violet: { stroke: "#262626", dot: "#262626" },
  };

  const activeColor = colorMap[color] || { stroke: "#FF3700", dot: "#FF3700" };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let offset = 0;

    const handleResize = () => {
      if (!canvas) return;
      canvas.width = canvas.parentElement?.clientWidth || 250;
      canvas.height = 70;
    };
    handleResize();
    window.addEventListener("resize", handleResize);

    const interval = setInterval(() => {
      if (typeof value === "number") {
        const delta = (Math.random() - 0.5) * (value * 0.05);
        const newVal = value + delta;
        setLiveVal(newVal.toFixed(1));
      }
    }, 1200);

    const draw = () => {
      if (!ctx || !canvas) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const w = canvas.width;
      const h = canvas.height;

      // Subtle Hanzo hairline grid lines
      ctx.strokeStyle = "rgba(0, 0, 0, 0.04)";
      ctx.lineWidth = 0.5;
      for (let y = 10; y < h; y += 15) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      ctx.lineWidth = 1.8;
      ctx.strokeStyle = activeColor.stroke;

      if (type === "sine") {
        ctx.beginPath();
        ctx.moveTo(0, h / 2);
        for (let x = 0; x < w; x += 3) {
          const y = h / 2 + Math.sin((x + offset) * 0.05) * 16;
          ctx.lineTo(x, y);
        }
        ctx.stroke();
      } else if (type === "bars") {
        const barWidth = 5;
        const gap = 4;
        const count = Math.floor(w / (barWidth + gap));
        for (let i = 0; i < count; i++) {
          const bh = 8 + Math.sin((i + offset * 0.1) * 0.5) * 18 + Math.random() * 6;
          ctx.fillStyle = activeColor.stroke;
          ctx.fillRect(i * (barWidth + gap), h - bh, barWidth, bh);
        }
      } else {
        ctx.beginPath();
        ctx.moveTo(0, h / 2);
        for (let x = 0; x < w; x += 10) {
          const y = h / 2 + (Math.random() - 0.5) * 24;
          ctx.lineTo(x, y);
        }
        ctx.stroke();
      }

      offset += 1.5;
      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener("resize", handleResize);
      clearInterval(interval);
      cancelAnimationFrame(animationFrameId);
    };
  }, [value, type, activeColor.stroke]);

  return (
    <div className="p-6 sm:p-7 rounded-3xl bg-white border border-[#D9D9D9] hover:border-[#000000] transition-all duration-300 shadow-xs flex flex-col justify-between min-h-[220px]">
      <div className="flex items-center justify-between mb-2">
        <span className="font-mono text-xs font-bold text-[#545454] uppercase tracking-wider">
          {title}
        </span>
        <span
          className="w-2 h-2 rounded-full animate-pulse"
          style={{ backgroundColor: activeColor.dot }}
        />
      </div>

      <div className="flex items-baseline gap-1.5 my-2">
        <span className="font-display font-extrabold text-3xl sm:text-4xl text-[#000000] tracking-tight">
          {liveVal}
        </span>
        {unit && (
          <span className="font-mono text-xs text-[#545454] font-semibold">{unit}</span>
        )}
      </div>

      <div className="w-full my-2 overflow-hidden rounded-xl bg-[#FAFAF9] p-1 border border-[#D9D9D9]/50">
        <canvas ref={canvasRef} className="w-full h-[65px]" />
      </div>

      {subtext && (
        <span className="font-mono text-[10px] text-[#545454] tracking-wider uppercase font-medium">
          {subtext}
        </span>
      )}
    </div>
  );
}
