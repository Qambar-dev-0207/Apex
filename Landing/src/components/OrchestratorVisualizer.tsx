"use client";

import { useEffect, useRef } from "react";

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
  glow: number;
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

interface MatrixStream {
  x: number;
  y: number;
  speed: number;
  chars: string[];
}

// Complex Inter-Node Connection Link Matrix
const NEURAL_LINKS: VisualLink[] = [
  // Center Core outbound lines (Hub & Spoke)
  { from: 0, to: 1 },
  { from: 0, to: 2 },
  { from: 0, to: 3 },
  { from: 0, to: 4 },
  { from: 0, to: 5 },
  { from: 0, to: 6 },

  // Tier 1 Ring (Brain)
  { from: 1, to: 2 },
  { from: 2, to: 3 },
  { from: 3, to: 1 },

  // Tier 2 Ring (Memory)
  { from: 4, to: 5 },
  { from: 5, to: 6 },
  { from: 6, to: 4 },

  // Tier 3 Ring (Execution)
  { from: 7, to: 8 },
  { from: 8, to: 9 },
  { from: 9, to: 7 },

  // Cross-Tier Vertical Pipe Links
  { from: 1, to: 4 }, // Intent Router -> Semantic Cache
  { from: 2, to: 5 }, // Socratic Gate -> Vector DB
  { from: 3, to: 9 }, // Steelman -> Swarm Research
  { from: 4, to: 7 }, // Cache -> Parallel Dispatch
  { from: 5, to: 8 }, // Vector DB -> Sandbox Engine
  { from: 7, to: 10 }, // Dispatch -> Hardware Bridge
  { from: 8, to: 11 }  // Sandbox -> Vision Retina
];

export default function OrchestratorVisualizer({ activePreset, isSimulating }: VisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef<{ x: number; y: number }>({ x: -1000, y: -1000 });

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
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let time = 0;
    
    // Core accumulated angles for manual rotation
    let accumX = 0;
    let accumY = 0;

    // Smoothed parallax camera tilts (LERP target tracking)
    let smoothTiltX = 0;
    let smoothTiltY = 0;

    const baseAngleX = 0.0018;
    const baseAngleY = 0.0032;
    const fov = 300;
    
    // Nodes scaled up by 1.35x to populate the larger canvas area (with static initialX/Y/Z)
    const nodes: VisualNode[] = [
      // Center Brain Node
      { x: 0, y: 0, z: 0, initialX: 0, initialY: 0, initialZ: 0, radius: 12, label: "ORCHESTRATOR CORE", tier: "brain", color: "#0C0C0E", glow: 1 },
      
      // Tier 1: Brain Nodes (Inner Ring)
      { x: 0, y: 0, z: 0, initialX: -60, initialY: -34, initialZ: 14, radius: 7, label: "Intent Router", tier: "brain", color: "#00F0FF", glow: 0.3 },
      { x: 0, y: 0, z: 0, initialX: 60, initialY: -34, initialZ: -14, radius: 7, label: "Socratic Gate", tier: "brain", color: "#FF5000", glow: 0.3 },
      { x: 0, y: 0, z: 0, initialX: 34, initialY: 54, initialZ: 40, radius: 7, label: "Steelman Strategy", tier: "brain", color: "#FF5000", glow: 0.3 },
      
      // Tier 2: Memory Nodes (Middle Ring)
      { x: 0, y: 0, z: 0, initialX: -115, initialY: 20, initialZ: -60, radius: 6, label: "Semantic Cache", tier: "memory", color: "#8A4FFF", glow: 0.3 },
      { x: 0, y: 0, z: 0, initialX: 115, initialY: 20, initialZ: 60, radius: 6, label: "Chroma VectorDB", tier: "memory", color: "#8A4FFF", glow: 0.3 },
      { x: 0, y: 0, z: 0, initialX: -40, initialY: -95, initialZ: -27, radius: 6, label: "Cognitive Graph", tier: "memory", color: "#8A4FFF", glow: 0.3 },
      
      // Tier 3: Execution Nodes (Outer Ring)
      { x: 0, y: 0, z: 0, initialX: -155, initialY: -54, initialZ: 80, radius: 6.5, label: "Parallel Dispatch", tier: "execution", color: "#00FF87", glow: 0.2 },
      { x: 0, y: 0, z: 0, initialX: 155, initialY: -54, initialZ: -80, radius: 6.5, label: "Sandbox Engine", tier: "execution", color: "#00FF87", glow: 0.2 },
      { x: 0, y: 0, z: 0, initialX: 80, initialY: 120, initialZ: -40, radius: 6.5, label: "Swarm Research", tier: "execution", color: "#00FF87", glow: 0.2 },

      // Tier 4: Vitals Nodes (Outer Edge)
      { x: 0, y: 0, z: 0, initialX: -180, initialY: 68, initialZ: -47, radius: 5.5, label: "Hardware Bridge", tier: "vitals", color: "#FFB000", glow: 0.2 },
      { x: 0, y: 0, z: 0, initialX: 180, initialY: 68, initialZ: 47, radius: 5.5, label: "Vision Retina", tier: "vitals", color: "#FFB000", glow: 0.2 }
    ];

    let pathParticles: PathParticle[] = [];
    const streams: MatrixStream[] = [];
    const streamCount = 8;

    // Initialize falling matrix streams
    for (let i = 0; i < streamCount; i++) {
      const isLeft = i < streamCount / 2;
      streams.push({
        x: isLeft ? Math.random() * 50 + 15 : 280 + Math.random() * 50,
        y: Math.random() * 320,
        speed: 1.0 + Math.random() * 1.8,
        chars: Array.from({ length: 6 }, () => {
          const rand = Math.random();
          if (rand < 0.3) return "01";
          if (rand < 0.6) return "0x";
          return "ok";
        })
      });
    }

    const handleResize = () => {
      if (!canvas) return;
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
    };

    const hexToRgba = (hex: string, alpha: number) => {
      const cleanHex = hex.replace("#", "");
      const r = parseInt(cleanHex.substring(0, 2), 16);
      const g = parseInt(cleanHex.substring(2, 4), 16);
      const b = parseInt(cleanHex.substring(4, 6), 16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    };

    const isNodeActive = (nodeLabel: string) => {
      const labelLower = nodeLabel.toLowerCase();
      if (activePreset === "router" && labelLower.includes("router")) return true;
      if (activePreset === "cache" && (labelLower.includes("cache") || labelLower.includes("vector"))) return true;
      if (activePreset === "socratic" && (labelLower.includes("socratic") || labelLower.includes("steelman"))) return true;
      if (activePreset === "swarm" && (labelLower.includes("dispatch") || labelLower.includes("swarm"))) return true;
      if (activePreset === "sandbox" && labelLower.includes("sandbox")) return true;
      if (activePreset === "verifier" && labelLower.includes("core")) return true;
      return false;
    };

    handleResize();
    window.addEventListener("resize", handleResize);

    const rotatePoint = (px: number, py: number, pz: number, rotAngleX: number, rotAngleY: number) => {
      const y1 = py * Math.cos(rotAngleX) - pz * Math.sin(rotAngleX);
      const z1 = py * Math.sin(rotAngleX) + pz * Math.cos(rotAngleX);

      const x2 = px * Math.cos(rotAngleY) - z1 * Math.sin(rotAngleY);
      const z2 = px * Math.sin(rotAngleY) + z1 * Math.cos(rotAngleY);

      return { x: x2, y: y1, z: z2 };
    };

    const draw = () => {
      if (!ctx || !canvas) return;
      const width = canvas.width / (window.devicePixelRatio || 1);
      const height = canvas.height / (window.devicePixelRatio || 1);

      ctx.clearRect(0, 0, width, height);

      time += isSimulating ? 0.08 : 0.03;

      let speedMult = 1.0;
      if (isSimulating) speedMult = 3.5;
      else if (activePreset === "cache") speedMult = 0.5;
      else if (activePreset === "socratic") speedMult = 1.6;

      const currentAngleX = baseAngleX * speedMult;
      const currentAngleY = baseAngleY * speedMult;

      accumX += currentAngleX;
      accumY += currentAngleY;

      const cx = width / 2;
      const cy = height / 2 - 20;

      // 1. Mouse interactive parallax tilt LERP
      const mouse = mouseRef.current;
      const mouseOffset = {
        x: mouse.x === -1000 ? 0 : (mouse.x - cx) / Math.max(1, width),
        y: mouse.y === -1000 ? 0 : (mouse.y - cy) / Math.max(1, height)
      };

      const targetTiltX = mouseOffset.y * 0.5; // Pitch
      const targetTiltY = -mouseOffset.x * 0.5; // Roll

      smoothTiltX += (targetTiltX - smoothTiltX) * 0.1;
      smoothTiltY += (targetTiltY - smoothTiltY) * 0.1;

      // Apply combined rotations (accumulated + smooth mouse tilt) from node starting coordinates
      nodes.forEach((node) => {
        const rotated = rotatePoint(node.initialX, node.initialY, node.initialZ, accumX + smoothTiltX, accumY + smoothTiltY);
        node.x = rotated.x;
        node.y = rotated.y;
        node.z = rotated.z;

        // Trail coordinates calculated dynamically in the render phase below

        if (isSimulating) {
          node.glow = Math.min(1.0, node.glow + 0.05);
        } else {
          node.glow = Math.max(node.tier === "brain" ? 0.8 : 0.3, node.glow - 0.01);
        }
      });

      const sortedNodes = [...nodes].sort((a, b) => b.z - a.z);

      // 2. Telemetry Cartesian / Polar backdrop grid
      ctx.save();
      ctx.strokeStyle = "rgba(12, 12, 14, 0.02)";
      ctx.lineWidth = 0.5;
      
      // Dotted Concentric rings
      ctx.setLineDash([2, 4]);
      for (let r = 80; r <= 280; r += 60) {
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.setLineDash([]);

      // Solid Axes with ticks
      ctx.beginPath();
      ctx.moveTo(cx - 300, cy); ctx.lineTo(cx + 300, cy);
      ctx.moveTo(cx, cy - 200); ctx.lineTo(cx, cy + 200);
      ctx.stroke();

      // Axis label coordinates ticks
      ctx.font = "600 5.5px var(--font-mono)";
      ctx.fillStyle = "rgba(12, 12, 14, 0.15)";
      ctx.fillText("N // 0.0", cx + 4, cy - 190);
      ctx.fillText("S // 1.8", cx + 4, cy + 194);
      ctx.fillText("W // 2.7", cx - 295, cy - 4);
      ctx.fillText("E // 0.9", cx + 265, cy - 4);
      ctx.restore();

      // 3. Draw falling Matrix Stream specs
      streams.forEach((stream) => {
        stream.y += stream.speed * (isSimulating ? 2.5 : 1.0);
        if (stream.y > height) {
          stream.y = -50;
          stream.x = Math.random() < 0.5 ? Math.random() * 55 + 15 : width - (Math.random() * 55 + 70);
        }

        ctx.font = `600 6px var(--font-mono)`;
        ctx.fillStyle = isSimulating ? "rgba(255, 80, 0, 0.07)" : "rgba(12, 12, 14, 0.024)";
        ctx.textAlign = "left";

        stream.chars.forEach((char, cIdx) => {
          const charY = stream.y + cIdx * 8;
          if (charY > 0 && charY < height - 32) {
            ctx.fillText(char, stream.x, charY);
          }
        });
      });

      // 4. Concentric 3D projected orbit rings (Scaled up)
      const drawConcentric3DOrbit = (ringRadius: number) => {
        ctx.beginPath();
        for (let j = 0; j <= 64; j++) {
          const angle = (j / 64) * Math.PI * 2;
          const px = Math.cos(angle) * ringRadius;
          const pz = Math.sin(angle) * ringRadius;
          const py = 0;

          // Rotate points including smooth parallax tilts
          const rotated = rotatePoint(px, py, pz, accumX + smoothTiltX, accumY + smoothTiltY);
          const scale = fov / (fov + rotated.z);
          const sx = cx + rotated.x * scale;
          const sy = cy + rotated.y * scale;

          if (j === 0) ctx.moveTo(sx, sy);
          else ctx.lineTo(sx, sy);
        }
        ctx.lineWidth = 0.55;
        ctx.strokeStyle = isSimulating 
          ? "rgba(255, 80, 0, 0.12)" 
          : "rgba(12, 12, 14, 0.04)";
        ctx.stroke();
      };

      drawConcentric3DOrbit(80);
      drawConcentric3DOrbit(142);
      drawConcentric3DOrbit(210);

      // Oscilloscope wave
      ctx.beginPath();
      ctx.lineWidth = 0.9;
      ctx.strokeStyle = isSimulating ? "rgba(255, 80, 0, 0.45)" : "rgba(12, 12, 14, 0.08)";
      for (let x = 0; x < width; x++) {
        const waveAmp = isSimulating ? 15 : 6;
        const waveFreq = isSimulating ? 0.06 : 0.025;
        const yOffset = height - 28;
        const yVal = yOffset + Math.sin(x * waveFreq + time) * waveAmp * Math.sin(x * 0.003);
        if (x === 0) ctx.moveTo(x, yVal);
        else ctx.lineTo(x, yVal);
      }
      ctx.stroke();

      // Radar metrics indicators
      ctx.font = `600 7px var(--font-mono)`;
      ctx.fillStyle = "rgba(12, 12, 14, 0.35)";
      ctx.textAlign = "left";
      ctx.fillText(`AZIMUTH: ${(time * 18 % 360).toFixed(1)}°`, 20, height - 28);
      ctx.textAlign = "right";
      ctx.fillText(`ELEVATION: ${(15 + Math.sin(time * 0.4) * 5).toFixed(1)}°`, width - 20, height - 28);

      // 5. Draw Neural Web Links (Adjacent Meshes)
      ctx.save();
      NEURAL_LINKS.forEach((link) => {
        const nodeA = nodes[link.from];
        const nodeB = nodes[link.to];
        if (!nodeA || !nodeB) return;

        const scaleA = fov / (fov + nodeA.z);
        const scaleB = fov / (fov + nodeB.z);

        const ax = cx + nodeA.x * scaleA;
        const ay = cy + nodeA.y * scaleA;
        const bx = cx + nodeB.x * scaleB;
        const by = cy + nodeB.y * scaleB;

        const isLinkActive = isNodeActive(nodeA.label) || isNodeActive(nodeB.label);
        const avgZ = (nodeA.z + nodeB.z) / 2;
        
        // Depth-shaded opacity
        const depthOpacity = 0.02 + (1.0 - (avgZ + 150) / 300) * 0.15;
        const lineOpacity = isLinkActive ? 0.45 : depthOpacity;

        const grad = ctx.createLinearGradient(ax, ay, bx, by);
        grad.addColorStop(0, hexToRgba(nodeA.color, lineOpacity));
        grad.addColorStop(1, hexToRgba(nodeB.color, lineOpacity));

        ctx.beginPath();
        ctx.moveTo(ax, ay);
        ctx.lineTo(bx, by);
        ctx.lineWidth = isLinkActive ? 0.95 : 0.5;
        ctx.strokeStyle = grad;
        ctx.stroke();
      });
      ctx.restore();

      // 6. Path Particle Swarm execution flow along NEURAL_LINKS
      if (pathParticles.length < 32 && Math.random() < 0.18) {
        const randomLinkIdx = Math.floor(Math.random() * NEURAL_LINKS.length);
        const link = NEURAL_LINKS[randomLinkIdx];
        const color = nodes[link.to].color;
        pathParticles.push({
          linkIndex: randomLinkIdx,
          progress: 0,
          speed: 0.01 + Math.random() * 0.015 + (isSimulating ? 0.025 : 0.008),
          color: color
        });
      }

      // Draw Path Particles
      ctx.save();
      pathParticles = pathParticles.filter((p) => {
        p.progress += p.speed;
        if (p.progress >= 1.0) return false;

        const link = NEURAL_LINKS[p.linkIndex];
        const nodeA = nodes[link.from];
        const nodeB = nodes[link.to];

        // LERP coordinates in 3D
        const px = nodeA.x * (1.0 - p.progress) + nodeB.x * p.progress;
        const py = nodeA.y * (1.0 - p.progress) + nodeB.y * p.progress;
        const pz = nodeA.z * (1.0 - p.progress) + nodeB.z * p.progress;

        const pScale = fov / (fov + pz);
        const sx = cx + px * pScale;
        const sy = cy + py * pScale;

        ctx.shadowColor = p.color;
        ctx.shadowBlur = 4;
        ctx.beginPath();
        ctx.arc(sx, sy, 1.8 * pScale, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.fill();

        return true;
      });
      ctx.restore();

      // 7. Core HUD rotating telemetry indicators
      ctx.save();
      ctx.translate(cx, cy);
      
      // Rotating Compass dial
      ctx.rotate(-time * 0.15);
      ctx.strokeStyle = "rgba(12, 12, 14, 0.045)";
      ctx.lineWidth = 0.55;
      ctx.setLineDash([3, 9]);
      ctx.beginPath();
      ctx.arc(0, 0, 24, 0, Math.PI * 2);
      ctx.stroke();

      // Outer solid fine ring
      ctx.setLineDash([]);
      ctx.strokeStyle = "rgba(12, 12, 14, 0.015)";
      ctx.beginPath();
      ctx.arc(0, 0, 32, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();

      // Draw Nodes
      sortedNodes.forEach((node) => {
        const scale = fov / (fov + node.z);
        const screenX = cx + node.x * scale;
        const screenY = cy + node.y * scale;
        const size = node.radius * scale;

        const isActive = isNodeActive(node.label);

        // Distance check for hover detection
        const dx = screenX - mouse.x;
        const dy = screenY - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const isHovered = dist < size + 10;

        const coreBreathe = node.label === "ORCHESTRATOR CORE" 
          ? (1.0 + Math.sin(time * 2) * 0.1) 
          : 1.0;

        // Draw particle trail comets behind nodes (computed dynamically to prevent camera-tilt lagging)
        if (node.label !== "ORCHESTRATOR CORE") {
          for (let i = 1; i <= 8; i++) {
            const pastAccumX = accumX - i * currentAngleX;
            const pastAccumY = accumY - i * currentAngleY;
            const pos = rotatePoint(node.initialX, node.initialY, node.initialZ, pastAccumX + smoothTiltX, pastAccumY + smoothTiltY);
            
            const tScale = fov / (fov + pos.z);
            const tx = cx + pos.x * tScale;
            const ty = cy + pos.y * tScale;
            const opacity = (8 - i + 1) / 32 * (isSimulating ? 0.6 : 0.25);
            
            ctx.beginPath();
            ctx.arc(tx, ty, size * 0.35 * ((8 - i + 1) / 8), 0, Math.PI * 2);
            ctx.fillStyle = hexToRgba(node.color, opacity);
            ctx.fill();
          }
        }

        // Draw Node Core Circle
        ctx.save();
        ctx.shadowColor = node.color;
        ctx.shadowBlur = (isActive || isHovered ? 12 : node.glow * 4);
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 2;

        ctx.beginPath();
        ctx.arc(screenX, screenY, size * coreBreathe, 0, Math.PI * 2);
        ctx.fillStyle = node.color;
        ctx.fill();
        ctx.restore();

        // Node Inner Core Dot
        ctx.beginPath();
        ctx.arc(screenX, screenY, size * coreBreathe * 0.3, 0, Math.PI * 2);
        ctx.fillStyle = "#FFFFFF";
        ctx.fill();

        // Draw radial offset labels for active or hovered nodes
        if (isActive || isHovered) {
          const radAngle = Math.atan2(node.y, node.x);
          const textOffset = size + 28;
          const textX = screenX + Math.cos(radAngle) * textOffset;
          const textY = screenY + Math.sin(radAngle) * textOffset;

          // Leader line
          ctx.beginPath();
          ctx.moveTo(screenX + Math.cos(radAngle) * size, screenY + Math.sin(radAngle) * size);
          ctx.lineTo(textX - Math.cos(radAngle) * 4, textY - Math.sin(radAngle) * 4);
          ctx.strokeStyle = hexToRgba(node.color, 0.65);
          ctx.lineWidth = 0.5;
          ctx.setLineDash([1.5, 2]);
          ctx.stroke();
          ctx.setLineDash([]);

          // HUD target bracket rings
          ctx.save();
          ctx.strokeStyle = node.color;
          ctx.lineWidth = 0.8;
          ctx.beginPath();
          ctx.arc(screenX, screenY, size + 4, radAngle - Math.PI / 4, radAngle + Math.PI / 4);
          ctx.stroke();
          ctx.beginPath();
          ctx.arc(screenX, screenY, size + 4, radAngle + Math.PI - Math.PI / 4, radAngle + Math.PI + Math.PI / 4);
          ctx.stroke();
          ctx.restore();

          // Align text outwards radially
          ctx.font = `700 8.5px var(--font-mono)`;
          ctx.fillStyle = "#0C0C0E";
          if (Math.abs(Math.cos(radAngle)) < 0.25) {
            ctx.textAlign = "center";
          } else {
            ctx.textAlign = Math.cos(radAngle) > 0 ? "left" : "right";
          }
          
          ctx.fillText(node.label.toUpperCase(), textX, textY + 3);
          
          ctx.font = `600 6px var(--font-mono)`;
          ctx.fillStyle = hexToRgba(node.color, 0.95);
          ctx.fillText(`COGNITIVE STAGE`, textX, textY - 6);
        }
      });

      // 8. HUD Diagnositcs overlay texts in the canvas corners
      ctx.font = `600 6px var(--font-mono)`;
      ctx.fillStyle = "rgba(12, 12, 14, 0.3)";
      ctx.textAlign = "left";
      
      // Top Left Corner
      ctx.fillText(`SYS.MATRIX_TILT: [PX:${smoothTiltX.toFixed(2)}, RY:${smoothTiltY.toFixed(2)}]`, 16, 20);
      ctx.fillText(`SYS.NET_RATE: ${isSimulating ? "142Hz" : "45Hz"}`, 16, 28);
      ctx.fillText(`SYS.STATE: SIMULATION_RUN`, 16, 36);

      // Top Right Corner
      ctx.textAlign = "right";
      ctx.fillText(`NET.NODES_ALIVE: 12/12`, width - 16, 20);
      ctx.fillText(`NET.VECTORS: 1,240`, width - 16, 28);
      ctx.fillText(`NET.STAGE: active`, width - 16, 36);

      // Status text Overlay (bottom center)
      ctx.font = `500 8px var(--font-mono)`;
      ctx.fillStyle = isSimulating ? "#FF5000" : "#585862";
      ctx.textAlign = "center";
      if (isSimulating) {
        ctx.fillText("APEX ACTIVE CORE EXECUTING RUNTIME SIMULATION", cx, height - 10);
      } else {
        ctx.fillText(`OS STANDBY // ACTIVE MODEL ROUTE: ${activePreset.toUpperCase()}`, cx, height - 10);
      }

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", handleResize);
    };
  }, [activePreset, isSimulating]);

  return (
    <div className="relative w-full h-full flex items-center justify-center overflow-hidden">
      <canvas
        ref={canvasRef}
        className="w-full h-full block"
        style={{ minHeight: "450px" }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      />
      {/* Light HUD border notches */}
      <div className="absolute inset-4 border border-black/[0.03] pointer-events-none rounded-lg">
        <span className="absolute top-0 left-0 w-2 h-2 border-t border-l border-black/15"></span>
        <span className="absolute top-0 right-0 w-2 h-2 border-t border-r border-black/15"></span>
        <span className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-black/15"></span>
        <span className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-black/15"></span>
      </div>
    </div>
  );
}
