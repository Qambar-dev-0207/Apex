"use client";

import { useEffect, useRef, useState } from "react";

interface TelemetryCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  type: "sine" | "bars" | "random";
  color: "cyan" | "violet" | "emerald" | "amber";
}

export default function TelemetryCard({
  title,
  value,
  unit = "",
  subtext = "",
  type,
  color,
}: TelemetryCardProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [liveVal, setLiveVal] = useState<number | string>(value);

  const colorMap = {
    cyan: { base: "#2563EB", glow: "rgba(37, 99, 235, 0.15)", line: "#2563EB" },
    violet: { base: "#7C3AED", glow: "rgba(124, 58, 237, 0.15)", line: "#7C3AED" },
    emerald: { base: "#059669", glow: "rgba(5, 150, 105, 0.15)", line: "#059669" },
    amber: { base: "#FF4500", glow: "rgba(255, 69, 0, 0.15)", line: "#FF4500" },
  };

  const colors = colorMap[color] || colorMap.cyan;

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

      // Light Tech Grid Lines
      ctx.strokeStyle = "rgba(12, 12, 14, 0.04)";
      ctx.lineWidth = 0.5;
      for (let y = 10; y < h; y += 15) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      ctx.lineWidth = 1.8;
      ctx.strokeStyle = colors.line;

      if (type === "sine") {
        ctx.beginPath();
        ctx.moveTo(0, h / 2);
        for (let x = 0; x < w; x += 3) {
          const y = h / 2 + Math.sin((x + offset) * 0.05) * 16;
          ctx.lineTo(x, y);
        }
        ctx.stroke();
      } else if (type === "bars") {
        const barWidth = 6;
        const gap = 4;
        const count = Math.floor(w / (barWidth + gap));
        for (let i = 0; i < count; i++) {
          const bh = 10 + Math.sin((i + offset * 0.1) * 0.5) * 20 + Math.random() * 8;
          ctx.fillStyle = colors.line;
          ctx.fillRect(i * (barWidth + gap), h - bh, barWidth, bh);
        }
      } else {
        ctx.beginPath();
        ctx.moveTo(0, h / 2);
        for (let x = 0; x < w; x += 10) {
          const y = h / 2 + (Math.random() - 0.5) * 28;
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
  }, [value, type, color, colors.line]);

  return (
    <div className="editorial-card p-5 flex flex-col justify-between">
      <div className="flex items-center justify-between mb-2">
        <span className="font-display font-semibold text-xs text-[#0C0C0E] uppercase tracking-wider">
          {title}
        </span>
        <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: colors.line }}></span>
      </div>

      <div className="flex items-baseline gap-1.5 my-1">
        <span className="font-mono text-2xl font-extrabold text-[#0C0C0E] tracking-tight">
          {liveVal}
        </span>
        {unit && <span className="font-mono text-xs text-[#71717A] font-semibold">{unit}</span>}
      </div>

      <div className="w-full my-2 overflow-hidden rounded">
        <canvas ref={canvasRef} className="w-full h-[70px]" />
      </div>

      {subtext && (
        <span className="font-mono text-[10px] text-[#71717A] mt-1 block tracking-wider font-medium">
          {subtext}
        </span>
      )}
    </div>
  );
}
