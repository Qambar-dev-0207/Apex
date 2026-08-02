"use client";

import { useEffect, useRef, useState } from "react";

interface VisualizerProps {
  activePreset: string;
  isSimulating: boolean;
}

interface VisualNode {
  x: number;
  y: number;
  z: number;
  initialX: number;
  initialY: number;
  initialZ: number;
  radius: number;
  label: string;
  tier: "brain" | "memory" | "execution" | "vitals";
  color: string;
}

interface VisualLink {
  from: number;
  to: number;
}

interface PathParticle {
  linkIndex: number;
  progress: number;
  speed: number;
  color: string;
}

const NEURAL_LINKS: VisualLink[] = [
  { from: 0, to: 1 },
  { from: 0, to: 2 },
  { from: 0, to: 3 },
  { from: 0, to: 4 },
  { from: 0, to: 5 },
  { from: 0, to: 6 },
  { from: 1, to: 2 },
  { from: 2, to: 3 },
  { from: 3, to: 1 },
  { from: 4, to: 5 },
  { from: 5, to: 6 },
  { from: 6, to: 4 },
  { from: 7, to: 8 },
  { from: 8, to: 9 },
  { from: 9, to: 7 },
  { from: 1, to: 4 },
  { from: 2, to: 5 },
  { from: 3, to: 9 },
  { from: 4, to: 7 },
  { from: 5, to: 8 },
  { from: 7, to: 10 },
  { from: 8, to: 11 }
];

export default function OrchestratorVisualizer({ activePreset, isSimulating }: VisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef<{ x: number; y: number }>({ x: -1000, y: -1000 });
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    mouseRef.current = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  };

  const handleMouseLeave = () => {
    mouseRef.current = { x: -1000, y: -1000 };
    setHoveredNode(null);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let angleY = 0;

    const nodes: VisualNode[] = [
      { x: 0, y: 0, z: 0, initialX: 0, initialY: 0, initialZ: 0, radius: 10, label: "APEX CORE", tier: "brain", color: "#FF4500" },
      { x: -130, y: -70, z: 50, initialX: -130, initialY: -70, initialZ: 50, radius: 7, label: "Intent Router", tier: "brain", color: "#2563EB" },
      { x: 130, y: -70, z: -30, initialX: 130, initialY: -70, initialZ: -30, radius: 7, label: "Socratic Gate", tier: "brain", color: "#FF4500" },
      { x: 0, y: -110, z: 80, initialX: 0, initialY: -110, initialZ: 80, radius: 7, label: "Steelman Engine", tier: "brain", color: "#7C3AED" },
      { x: -150, y: 30, z: -60, initialX: -150, initialY: 30, initialZ: -60, radius: 6.5, label: "ChromaDB Memory", tier: "memory", color: "#0284C7" },
      { x: 150, y: 30, z: 60, initialX: 150, initialY: 30, initialZ: 60, radius: 6.5, label: "Redis Cache", tier: "memory", color: "#059669" },
      { x: 0, y: 120, z: -50, initialX: 0, initialY: 120, initialZ: -50, radius: 6.5, label: "Code Compass", tier: "memory", color: "#2563EB" },
      { x: -100, y: 100, z: 90, initialX: -100, initialY: 100, initialZ: 90, radius: 6, label: "Parallel Dispatch", tier: "execution", color: "#7C3AED" },
      { x: 100, y: 100, z: -80, initialX: 100, initialY: 100, initialZ: -80, radius: 6, label: "Sandbox Engine", tier: "execution", color: "#DC2626" },
      { x: -130, y: -40, z: -90, initialX: -130, initialY: -40, initialZ: -90, radius: 6, label: "Agent Swarm", tier: "execution", color: "#FF4500" },
      { x: 130, y: -40, z: 100, initialX: 130, initialY: -40, initialZ: 100, radius: 6, label: "Hardware Bridge", tier: "vitals", color: "#059669" },
      { x: 0, y: 60, z: 130, initialX: 0, initialY: 60, initialZ: 130, radius: 6, label: "Vision Retina", tier: "vitals", color: "#0284C7" }
    ];

    const particles: PathParticle[] = Array.from({ length: 24 }, () => ({
      linkIndex: Math.floor(Math.random() * NEURAL_LINKS.length),
      progress: Math.random(),
      speed: 0.005 + Math.random() * 0.008,
      color: Math.random() > 0.5 ? "#FF4500" : "#2563EB"
    }));

    const resizeCanvas = () => {
      if (!canvas) return;
      canvas.width = canvas.parentElement?.clientWidth || 650;
      canvas.height = 420;
    };
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    const render = () => {
      if (!ctx || !canvas) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const focalLength = 350;

      angleY += isSimulating ? 0.006 : 0.002;

      // Project 3D to 2D with STRICT scale clamping
      const projectedNodes = nodes.map((node) => {
        const cos = Math.cos(angleY);
        const sin = Math.sin(angleY);

        const rx = node.initialX * cos - node.initialZ * sin;
        const rz = node.initialX * sin + node.initialZ * cos;
        const ry = node.initialY;

        const rawScale = focalLength / (focalLength + rz);
        const scale = Math.min(1.25, Math.max(0.65, rawScale));

        const px = centerX + rx * scale;
        const py = centerY + ry * scale;

        return { ...node, px, py, scale, rz };
      });

      projectedNodes.sort((a, b) => b.rz - a.rz);

      // Draw Links
      NEURAL_LINKS.forEach((link) => {
        const fromNode = projectedNodes.find(n => n.label === nodes[link.from].label);
        const toNode = projectedNodes.find(n => n.label === nodes[link.to].label);

        if (fromNode && toNode) {
          ctx.beginPath();
          ctx.moveTo(fromNode.px, fromNode.py);
          ctx.lineTo(toNode.px, toNode.py);
          ctx.strokeStyle = "rgba(12, 12, 14, 0.1)";
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      });

      // Draw Signal Pulse Particles
      particles.forEach((p) => {
        const link = NEURAL_LINKS[p.linkIndex];
        const fromNode = projectedNodes.find(n => n.label === nodes[link.from].label);
        const toNode = projectedNodes.find(n => n.label === nodes[link.to].label);

        if (fromNode && toNode) {
          p.progress += p.speed;
          if (p.progress > 1) p.progress = 0;

          const px = fromNode.px + (toNode.px - fromNode.px) * p.progress;
          const py = fromNode.py + (toNode.py - fromNode.py) * p.progress;

          ctx.beginPath();
          ctx.arc(px, py, 2.5, 0, Math.PI * 2);
          ctx.fillStyle = p.color;
          ctx.fill();
        }
      });

      // Draw Nodes & Labels
      let foundHover: string | null = null;
      projectedNodes.forEach((node) => {
        const r = node.radius * node.scale;

        const dx = mouseRef.current.x - node.px;
        const dy = mouseRef.current.y - node.py;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const isHovered = dist < r + 8;
        if (isHovered) foundHover = node.label;

        // Outer Glow Ring
        ctx.beginPath();
        ctx.arc(node.px, node.py, r + (isHovered ? 6 : 3), 0, Math.PI * 2);
        ctx.fillStyle = `${node.color}${isHovered ? '40' : '20'}`;
        ctx.fill();

        // Node Core Circle
        ctx.beginPath();
        ctx.arc(node.px, node.py, r, 0, Math.PI * 2);
        ctx.fillStyle = isHovered ? "#0C0C0E" : node.color;
        ctx.fill();

        // Label
        ctx.font = `600 ${Math.max(9, Math.min(12, 11 * node.scale))}px "JetBrains Mono", monospace`;
        ctx.fillStyle = isHovered ? "#FF4500" : "#0C0C0E";
        ctx.fillText(node.label, node.px + r + 5, node.py + 4);
      });

      setHoveredNode(foundHover);
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, [activePreset, isSimulating]);

  return (
    <div className="relative w-full h-[420px] bg-white border border-black/8 rounded-2xl overflow-hidden shadow-md">
      <div className="absolute top-3 left-4 z-10 flex items-center gap-2.5">
        <span className="w-2 h-2 rounded-full bg-[#FF4500] animate-ping"></span>
        <span className="font-mono text-[11px] font-semibold text-[#0C0C0E] uppercase tracking-wider">
          LIVE DAG • {activePreset.toUpperCase()}
        </span>
      </div>

      <canvas
        ref={canvasRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="w-full h-full cursor-crosshair"
      />

      {hoveredNode && (
        <div className="absolute bottom-3 left-4 z-10 bg-[#0C0C0E] text-white px-3 py-1 rounded-lg text-[11px] font-mono shadow-md">
          ACTIVE NODE: <span className="text-[#FF4500] font-bold">{hoveredNode}</span>
        </div>
      )}
    </div>
  );
}
