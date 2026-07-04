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

export default function TelemetryCard({ title, value, unit = "", subtext = "", type, color }: TelemetryCardProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [liveVal, setLiveVal] = useState<number | string>(value);

  // Colors adapted to the minimalist light-sand console scheme
  const colorMap = {
    cyan: { base: "#00B0FF", glow: "rgba(0, 176, 255, 0.08)", line: "rgba(0, 176, 255, 0.35)" },
    violet: { base: "#8A4FFF", glow: "rgba(138, 79, 255, 0.08)", line: "rgba(138, 79, 255, 0.35)" },
    emerald: { base: "#00D060", glow: "rgba(0, 208, 96, 0.08)", line: "rgba(0, 208, 96, 0.35)" },
    amber: { base: "#FF8F00", glow: "rgba(255, 143, 0, 0.08)", line: "rgba(255, 143, 0, 0.35)" }
  };

  const colors = colorMap[color] || colorMap.cyan;
  const { base, glow, line } = colors;

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
      canvas.height = 75;
    };
    handleResize();
    window.addEventListener("resize", handleResize);

    // Dynamic numerical simulation
    const interval = setInterval(() => {
      if (typeof value === "number") {
        const delta = (Math.random() - 0.5) * (value * 0.04);
        const newVal = value + delta;
        
        if (value > 90) {
          setLiveVal(newVal.toFixed(1));
        } else if (value > 10) {
          setLiveVal(newVal.toFixed(1));
        } else {
          setLiveVal(newVal.toFixed(2));
        }
      }
    }, 1500);

    const dataPoints: number[] = Array.from({ length: 30 }, () => Math.random() * 25 + 20);
    
    const draw = () => {
      if (!ctx || !canvas) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const w = canvas.width;
      const h = canvas.height;

      // 1. Draw technical oscilloscope grid lines
      ctx.strokeStyle = "rgba(12, 12, 14, 0.018)";
      ctx.lineWidth = 0.5;
      
      // Horizontal grid lines
      for (let y = 10; y < h; y += 15) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }
      // Vertical grid lines
      for (let x = 10; x < w; x += 25) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }

      ctx.lineWidth = 1.3;

      if (type === "sine") {
        // Draw modulated scrolling sine waves
        ctx.beginPath();
        ctx.strokeStyle = base;
        ctx.moveTo(0, h / 2);
        
        let peakY = h;
        let peakX = 0;

        for (let x = 0; x < w; x++) {
          const y = h / 2 + Math.sin(x * 0.035 + offset) * 16 + Math.sin(x * 0.015 + offset * 0.5) * 6;
          ctx.lineTo(x, y);

          if (y < peakY) {
            peakY = y;
            peakX = x;
          }
        }
        ctx.stroke();

        // Draw Peak target dot
        ctx.beginPath();
        ctx.arc(peakX, peakY, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = base;
        ctx.fill();

        offset += 0.035;
      } else if (type === "bars") {
        // Technical spectrum bars
        const barWidth = 3;
        const gap = 3;
        const totalBars = Math.floor(w / (barWidth + gap));
        offset += 0.045;

        for (let i = 0; i < totalBars; i++) {
          const osc = Math.sin(i * 0.18 + offset) * Math.cos(i * 0.06 + offset * 0.3);
          const barHeight = Math.abs(osc) * (h * 0.65) + 6;
          
          const x = i * (barWidth + gap);
          const y = h - barHeight;

          ctx.fillStyle = i / totalBars > 0.82 ? line : base;
          ctx.fillRect(x, y, barWidth, barHeight);
        }
      } else {
        // Random scrolling sparkline with shadow area fill
        offset += 0.1;
        if (offset > 1.0) {
          offset = 0;
          dataPoints.shift();
          dataPoints.push(Math.random() * (h * 0.55) + h * 0.2);
        }

        ctx.beginPath();
        ctx.strokeStyle = base;
        const step = w / (dataPoints.length - 1);
        
        let peakY = h;
        let peakX = 0;

        ctx.moveTo(0, dataPoints[0]);
        for (let i = 1; i < dataPoints.length; i++) {
          const x = i * step;
          const y = dataPoints[i];
          ctx.lineTo(x, y);

          if (y < peakY) {
            peakY = y;
            peakX = x;
          }
        }
        ctx.stroke();

        // Area Gradient under curve
        const areaGrad = ctx.createLinearGradient(0, 0, 0, h);
        areaGrad.addColorStop(0, glow);
        areaGrad.addColorStop(1, "rgba(0, 0, 0, 0)");
        
        ctx.lineTo(w, h);
        ctx.lineTo(0, h);
        ctx.fillStyle = areaGrad;
        ctx.fill();

        // Draw Peak dot
        ctx.beginPath();
        ctx.arc(peakX, peakY, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = base;
        ctx.fill();
      }

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animationFrameId);
      clearInterval(interval);
      window.removeEventListener("resize", handleResize);
    };
  }, [value, type, base, glow, line]);

  return (
    <div 
      className="cockpit-panel p-4 flex flex-col justify-between overflow-hidden relative" 
      style={{ 
        minHeight: "152px", 
        backgroundColor: "var(--bg-cockpit)",
        borderColor: "var(--border-dim)"
      }}
    >
      {/* HUD corner notches */}
      <div className="absolute inset-0 pointer-events-none rounded-lg">
        <span className="absolute top-0 left-0 w-1.5 h-1.5 border-t border-l border-black/15"></span>
        <span className="absolute top-0 right-0 w-1.5 h-1.5 border-t border-r border-black/15"></span>
        <span className="absolute bottom-0 left-0 w-1.5 h-1.5 border-b border-l border-black/15"></span>
        <span className="absolute bottom-0 right-0 w-1.5 h-1.5 border-b border-r border-black/15"></span>
      </div>
      
      <div className="flex justify-between items-start z-10">
        <div>
          <span 
            className="text-[9px] uppercase tracking-wider font-mono"
            style={{ color: "var(--text-secondary)", fontWeight: 700 }}
          >
            {title}
          </span>
          <div className="flex items-baseline gap-1 mt-1">
            <span 
              className="text-xl font-bold font-mono tracking-tight"
              style={{ color: "var(--text-primary)" }}
            >
              {liveVal}
            </span>
            {unit && (
              <span 
                className="text-[9px] font-bold uppercase font-mono"
                style={{ color: "var(--text-muted)" }}
              >
                {unit}
              </span>
            )}
          </div>
        </div>
        
        {/* Pulsing indicator tag */}
        <span
          className="w-1.5 h-1.5 rounded-full"
          style={{
            backgroundColor: base,
            boxShadow: `0 0 6px ${base}`,
            opacity: 0.85
          }}
        ></span>
      </div>

      {/* Embedded Sparkline Canvas */}
      <div className="w-full h-[62px] mt-2 relative z-0 flex items-end">
        <canvas ref={canvasRef} className="w-full h-full block" />
      </div>

      {subtext && (
        <span 
          className="text-[8px] mt-2 block font-mono border-t pt-1"
          style={{ 
            color: "var(--text-muted)", 
            borderColor: "var(--border-dim)", 
            letterSpacing: "0.02em" 
          }}
        >
          {"// " + subtext.toUpperCase()}
        </span>
      )}
    </div>
  );
}
