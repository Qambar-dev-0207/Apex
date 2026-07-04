"use client";

import { useEffect, useRef } from "react";

interface Point3D {
  x: number;
  y: number;
  z: number;
}

export default function WireframeShapes() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef({ x: 0, y: 0, targetX: 0, targetY: 0, velocity: 0 });
  const prevMousePos = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let angle = 0;
    let twist = 0;

    const resize = () => {
      if (!canvas || !container) return;
      const dpr = window.devicePixelRatio || 1;
      canvas.width = container.clientWidth * dpr;
      canvas.height = container.clientHeight * dpr;
      ctx.scale(dpr, dpr);
    };
    resize();
    window.addEventListener("resize", resize);

    // 3D rotations
    const rotateX = (p: Point3D, a: number): Point3D => {
      const cos = Math.cos(a);
      const sin = Math.sin(a);
      return {
        x: p.x,
        y: p.y * cos - p.z * sin,
        z: p.y * sin + p.z * cos
      };
    };

    const rotateY = (p: Point3D, a: number): Point3D => {
      const cos = Math.cos(a);
      const sin = Math.sin(a);
      return {
        x: p.x * cos + p.z * sin,
        y: p.y,
        z: -p.x * sin + p.z * cos
      };
    };

    const rotateZ = (p: Point3D, a: number): Point3D => {
      const cos = Math.cos(a);
      const sin = Math.sin(a);
      return {
        x: p.x * cos - p.y * sin,
        y: p.x * sin + p.y * cos,
        z: p.z
      };
    };

    const project = (p: Point3D, w: number, h: number): { x: number; y: number; z: number } => {
      const fov = 200;
      const scale = fov / (fov + p.z);
      return {
        x: w / 2 + p.x * scale * 2.8,
        y: h / 2 + p.y * scale * 2.8,
        z: p.z
      };
    };

    const draw = () => {
      if (!ctx || !canvas) return;
      const width = canvas.width / (window.devicePixelRatio || 1);
      const height = canvas.height / (window.devicePixelRatio || 1);

      ctx.clearRect(0, 0, width, height);

      // Smooth mouse follow
      const mouse = mouseRef.current;
      mouse.x += (mouse.targetX - mouse.x) * 0.06;
      mouse.y += (mouse.targetY - mouse.y) * 0.06;

      // Decay velocity (twist effect)
      mouse.velocity *= 0.95;
      twist += (mouse.velocity * 0.05 - twist) * 0.08;

      // Base rotations
      const rX = mouse.y * 0.006 + angle;
      const rY = mouse.x * 0.006 + angle * 0.4;
      const rZ = angle * 0.2;

      // Mathematical Torus parametric variables
      const R = 38; // Major radius
      const baseR = 14; // Base minor radius
      const r = baseR + Math.sin(angle * 2) * 2; // Pulsing minor radius

      const rings = 16;
      const pointsPerRing = 12;
      const points: Point3D[] = [];

      for (let i = 0; i < rings; i++) {
        const u = (i / rings) * Math.PI * 2; // Angle around torus ring
        for (let j = 0; j < pointsPerRing; j++) {
          const v = (j / pointsPerRing) * Math.PI * 2 + u * twist; // Minor angle + twist phase
          
          points.push({
            x: (R + r * Math.cos(v)) * Math.cos(u),
            y: (R + r * Math.cos(v)) * Math.sin(u),
            z: r * Math.sin(v)
          });
        }
      }

      // Rotate and project points
      const projected = points.map((p) => {
        let rotated = rotateZ(p, rZ);
        rotated = rotateY(rotated, rY);
        rotated = rotateX(rotated, rX);
        return project(rotated, width, height);
      });

      // Draw lines
      ctx.lineWidth = 0.8;

      // Draw longitudinal rings
      for (let i = 0; i < rings; i++) {
        ctx.beginPath();
        // Shift colors based on depth (Z axis)
        const avgZ = points.slice(i * pointsPerRing, (i + 1) * pointsPerRing).reduce((acc, p) => acc + p.z, 0) / pointsPerRing;
        ctx.strokeStyle = avgZ > 0 
          ? "rgba(12, 12, 14, 0.05)" 
          : "rgba(255, 80, 0, 0.35)";

        for (let j = 0; j < pointsPerRing; j++) {
          const idx = i * pointsPerRing + j;
          const nextIdx = i * pointsPerRing + ((j + 1) % pointsPerRing);
          const p1 = projected[idx];
          const p2 = projected[nextIdx];
          
          if (j === 0) ctx.moveTo(p1.x, p1.y);
          else ctx.lineTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
        }
        ctx.stroke();
      }

      // Draw cross-connecting ribs
      ctx.beginPath();
      ctx.strokeStyle = "rgba(12, 12, 14, 0.08)";
      for (let j = 0; j < pointsPerRing; j++) {
        for (let i = 0; i < rings; i++) {
          const idx1 = i * pointsPerRing + j;
          const idx2 = ((i + 1) % rings) * pointsPerRing + j;
          const p1 = projected[idx1];
          const p2 = projected[idx2];
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
        }
      }
      ctx.stroke();

      // Highlight vertices (nodes) with micro circles
      projected.forEach((p, idx) => {
        if (idx % 3 === 0 && p.z < 0) { // Only front side nodes
          ctx.beginPath();
          ctx.arc(p.x, p.y, 1.5, 0, Math.PI * 2);
          ctx.fillStyle = "rgba(255, 80, 0, 0.7)";
          ctx.fill();
        }
      });

      // Draw mathematical telemetry corners
      ctx.font = "600 6px var(--font-mono)";
      ctx.fillStyle = "rgba(12, 12, 14, 0.28)";
      ctx.textAlign = "left";
      ctx.fillText(`ROT_X: ${rX.toFixed(2)} RAD`, 14, 18);
      ctx.fillText(`ROT_Y: ${rY.toFixed(2)} RAD`, 14, 26);
      ctx.fillText(`VEL: ${mouse.velocity.toFixed(2)} HZ`, 14, 34);

      ctx.textAlign = "right";
      ctx.fillText(`TORUS_R: ${R} PX`, width - 14, 18);
      ctx.fillText(`TORUS_r: ${r.toFixed(1)} PX`, width - 14, 26);
      ctx.fillText(`VERTICES: ${points.length}`, width - 14, 34);

      angle += 0.007;
      animationFrameId = requestAnimationFrame(draw);
    };

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const relativeX = e.clientX - rect.left - rect.width / 2;
      const relativeY = e.clientY - rect.top - rect.height / 2;
      
      const mouse = mouseRef.current;
      mouse.targetX = relativeX;
      mouse.targetY = relativeY;

      // Calculate mouse velocity (cursor acceleration)
      const dx = relativeX - prevMousePos.current.x;
      const dy = relativeY - prevMousePos.current.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      mouse.velocity = Math.min(25, mouse.velocity + dist * 0.15);

      prevMousePos.current.x = relativeX;
      prevMousePos.current.y = relativeY;
    };

    container.addEventListener("mousemove", handleMouseMove);
    draw();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", resize);
      if (container) {
        container.removeEventListener("mousemove", handleMouseMove);
      }
    };
  }, []);

  return (
    <div ref={containerRef} className="relative w-full h-full flex items-center justify-center">
      <canvas ref={canvasRef} className="w-full h-full block" />
    </div>
  );
}
